# File: routers/catches.py
from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File, Form
from typing import List
from bson import ObjectId
from datetime import datetime
from models.schemas import Catch, CatchCreate, CatchUpdate
from database import get_database
from auth import get_current_user, get_current_user_optional
from services.cloudinary_service import cloudinary_service

async def create_automatic_pin(catch_id: ObjectId, catch_data: dict, user_id: ObjectId, db):
    """Helper function to automatically create a pin when add_to_map is True"""
    try:
        # Check if pin already exists for this catch
        existing_pin = await db.pins.find_one({"catch_id": catch_id})
        if existing_pin:
            return  # Pin already exists, skip creation
        
        # Create pin data
        pin_data = {
            "catch_id": catch_id,
            "user_id": user_id,
            "location": catch_data["location"],
            "visibility": "public"  # Default to public, you can make this configurable
        }
        
        # Insert the pin
        await db.pins.insert_one(pin_data)
        
    except Exception as e:
        # Log the error but don't fail the catch creation
        print(f"Warning: Failed to create automatic pin: {e}")

router = APIRouter(prefix="/catches", tags=["catches"])

@router.post("/", response_model=Catch, status_code=status.HTTP_201_CREATED)
async def create_catch(
    catch_data: CatchCreate, 
    current_user = Depends(get_current_user),  # Require authentication
    db=Depends(get_database)
):
    """Upload new catch with JWT authentication"""
    try:
        # Create new catch using authenticated user
        catch_dict = catch_data.dict()
        catch_dict["user_id"] = current_user["_id"]  # Use authenticated user's ID
        catch_dict["created_at"] = datetime.utcnow()
        
        # Extract add_to_map flag before inserting
        add_to_map = catch_dict.pop("add_to_map", False)
        
        result = await db.catches.insert_one(catch_dict)
        created_catch = await db.catches.find_one({"_id": result.inserted_id})
        
        # Automatically create pin if add_to_map is True
        if add_to_map:
            await create_automatic_pin(
                catch_id=result.inserted_id,
                catch_data=catch_dict,
                user_id=current_user["_id"],
                db=db
            )
        
        return Catch(**created_catch)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create catch: {str(e)}"
        )

@router.post("/upload-with-image", response_model=Catch, status_code=status.HTTP_201_CREATED)
async def create_catch_with_image(
    file: UploadFile = File(...),
    species: str = Form(...),
    weight: float = Form(...),
    lat: float = Form(...),
    lng: float = Form(...),
    shared_with_followers: bool = Form(False),
    add_to_map: bool = Form(False),
    current_user = Depends(get_current_user),
    db=Depends(get_database)
):
    """Upload catch with image file - uploads to Cloudinary and creates catch in one step"""
    try:
        # Validate weight
        if weight <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Weight must be greater than 0"
            )
        
        # Validate species
        if not species or len(species.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Species name is required"
            )
        
        # Upload image to Cloudinary
        upload_result = await cloudinary_service.upload_image(file, folder="Rod Royale/catches")
        
        # Generate additional optimized URLs for different use cases
        public_id = upload_result["public_id"]
        thumbnail_url = cloudinary_service.generate_thumbnail_url(public_id, 300, 300)
        small_thumbnail_url = cloudinary_service.generate_thumbnail_url(public_id, 150, 150)
        optimized_url = cloudinary_service.generate_optimized_url(public_id, 800, 600)
        
        # Create catch data with Cloudinary URLs
        catch_dict = {
            "species": species.strip(),
            "weight": weight,
            "photo_url": upload_result["url"],  # Fix: use "url" not "secure_url"
            "photo_public_id": public_id,
            "thumbnail_url": thumbnail_url,
            "small_thumbnail_url": small_thumbnail_url,  # For map pins, lists
            "optimized_url": optimized_url,  # For detail views
            "location": {"lat": lat, "lng": lng},
            "shared_with_followers": shared_with_followers,
            "user_id": current_user["_id"],
            "created_at": datetime.utcnow()
        }
        
        # Save to database
        result = await db.catches.insert_one(catch_dict)
        created_catch = await db.catches.find_one({"_id": result.inserted_id})
        
        # Automatically create pin if add_to_map is True
        if add_to_map:
            await create_automatic_pin(
                catch_id=result.inserted_id,
                catch_data=catch_dict,
                user_id=current_user["_id"],
                db=db
            )
        
        return Catch(**created_catch)
        
    except HTTPException:
        raise
    except Exception as e:
        # If catch creation fails after image upload, we could clean up the image
        # but for now we'll let it remain in Cloudinary
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create catch with image: {str(e)}"
        )

@router.get("/feed", response_model=List[Catch])
async def get_user_feed(
    current_user = Depends(get_current_user),  # Require authentication
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_database)
):
    """Get user's personalized feed including their own catches and catches from users they follow"""
    try:
        # Get current user's ObjectId
        user_object_id = current_user["_id"]
        if not isinstance(user_object_id, ObjectId):
            user_object_id = ObjectId(user_object_id)
        
        # Get the current user's full profile to access following list
        user_profile = await db.users.find_one({"_id": user_object_id})
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Create list of user IDs to include in feed (user + following)
        feed_user_ids = [user_object_id]  # Include current user's catches
        
        # Add all users that the current user is following
        following_list = user_profile.get("following", [])
        for followed_user_id in following_list:
            if isinstance(followed_user_id, str):
                followed_user_id = ObjectId(followed_user_id)
            feed_user_ids.append(followed_user_id)
        
        # Query catches from all users in the feed (current user + following)
        # For current user: show all their catches (private and shared)
        # For followed users: only show catches shared with followers
        query = {
            "$or": [
                # Current user's catches (all of them, including private)
                {"user_id": user_object_id},
                # Followed users' catches (only those shared with followers)
                {
                    "user_id": {"$in": feed_user_ids[1:]},  # Exclude current user from this condition
                    "shared_with_followers": True
                }
            ]
        }
        cursor = db.catches.find(query).sort("created_at", -1).skip(skip).limit(limit)
        catches = await cursor.to_list(length=limit)
        
        return [Catch(**catch) for catch in catches]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user feed: {str(e)}"
        )

@router.get("/me", response_model=List[Catch])
async def get_my_catches(
    current_user = Depends(get_current_user),  # Require authentication
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_database)
):
    """Get current authenticated user's catches"""
    try:
        # Get all catches for the authenticated user (no filtering needed)
        user_object_id = current_user["_id"]
        if not isinstance(user_object_id, ObjectId):
            user_object_id = ObjectId(user_object_id)
            
        query = {"user_id": user_object_id}
        cursor = db.catches.find(query).sort("created_at", -1).skip(skip).limit(limit)
        catches = await cursor.to_list(length=limit)
        
        return [Catch(**catch) for catch in catches]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get your catches: {str(e)}"
        )

@router.get("/{catch_id}", response_model=Catch)
async def get_catch(
    catch_id: str, 
    current_user = Depends(get_current_user_optional),  # Optional authentication
    db=Depends(get_database)
):
    """Get single catch with access control based on JWT authentication"""
    try:
        if not ObjectId.is_valid(catch_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid catch ID format"
            )
        
        catch = await db.catches.find_one({"_id": ObjectId(catch_id)})
        if not catch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Catch not found"
            )
        
        # Access control logic
        if catch.get("shared_with_followers", False):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied - login required"
                )
            
            # Check if viewer is following the catch owner or is the owner
            viewer_id = current_user["_id"]
            catch_owner = await db.users.find_one({"_id": catch["user_id"]})
            
            # Allow if viewer is the owner
            if catch["user_id"] == viewer_id:
                return Catch(**catch)
            
            # Check if viewer is following the catch owner
            if catch_owner and viewer_id not in catch_owner.get("followers", []):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied - not following user"
                )
        
        return Catch(**catch)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get catch: {str(e)}"
        )

@router.get("/users/{user_id}/catches", response_model=List[Catch])
async def get_user_catches(
    user_id: str, 
    current_user = Depends(get_current_user),  # Require authentication
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_database)
):
    """List user's catches with pagination and access control (requires authentication)"""
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Check if user exists
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Build query based on access control
        query = {"user_id": ObjectId(user_id)}
        
        # If viewer is not the owner, filter based on sharing settings
        viewer_id = current_user["_id"]
        if ObjectId(user_id) != viewer_id:
            # Check if viewer is following this user
            is_follower = viewer_id in user.get("followers", [])
            if is_follower:
                # Show public catches and those shared with followers
                query["$or"] = [
                    {"shared_with_followers": {"$ne": True}},
                    {"shared_with_followers": True}
                ]
            else:
                # Show only public catches
                query["shared_with_followers"] = {"$ne": True}
        
        # Get catches with pagination
        cursor = db.catches.find(query).sort("created_at", -1).skip(skip).limit(limit)
        catches = await cursor.to_list(length=limit)
        
        return [Catch(**catch) for catch in catches]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user catches: {str(e)}"
        )

@router.put("/{catch_id}", response_model=Catch)
async def update_catch(
    catch_id: str, 
    catch_data: CatchUpdate, 
    current_user = Depends(get_current_user),  # Require authentication
    db=Depends(get_database)
):
    """Update catch (requires authentication - users can only update their own catches)"""
    try:
        if not ObjectId.is_valid(catch_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid catch ID format"
            )
        
        # Check if catch exists and belongs to user
        catch = await db.catches.find_one({"_id": ObjectId(catch_id)})
        if not catch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Catch not found"
            )
        
        # Ensure user can only update their own catches
        if catch["user_id"] != current_user["_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this catch"
            )
        
        # Prepare update data
        update_data = {k: v for k, v in catch_data.dict().items() if v is not None}
        
        if not update_data:
            return Catch(**catch)
        
        # Update catch
        await db.catches.update_one(
            {"_id": ObjectId(catch_id)},
            {"$set": update_data}
        )
        
        updated_catch = await db.catches.find_one({"_id": ObjectId(catch_id)})
        return Catch(**updated_catch)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update catch: {str(e)}"
        )

@router.delete("/{catch_id}")
async def delete_catch(
    catch_id: str, 
    current_user = Depends(get_current_user),  # Require authentication
    db=Depends(get_database)
):
    """Delete a catch (requires authentication - users can only delete their own catches)"""
    try:
        if not ObjectId.is_valid(catch_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid catch ID format"
            )
        
        # Check if catch exists and belongs to user
        catch = await db.catches.find_one({"_id": ObjectId(catch_id)})
        if not catch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Catch not found"
            )
        
        # Ensure user can only delete their own catches
        if catch["user_id"] != current_user["_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this catch"
            )
        
        # Delete catch
        await db.catches.delete_one({"_id": ObjectId(catch_id)})
        
        # Also delete associated pins
        await db.pins.delete_many({"catch_id": ObjectId(catch_id)})
        
        return {"message": "Catch deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete catch: {str(e)}"
        )
