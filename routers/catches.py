from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from models.schemas import Catch, CatchCreate, CatchUpdate
from database import get_database

router = APIRouter(prefix="/catches", tags=["catches"])

@router.post("/", response_model=Catch, status_code=status.HTTP_201_CREATED)
async def create_catch(catch_data: CatchCreate, user_id: str = Query(...), db=Depends(get_database)):
    """Upload new catch with image URL, species, etc."""
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
        
        # Create new catch
        catch_dict = catch_data.dict()
        catch_dict["user_id"] = ObjectId(user_id)
        catch_dict["created_at"] = datetime.utcnow()
        
        result = await db.catches.insert_one(catch_dict)
        created_catch = await db.catches.find_one({"_id": result.inserted_id})
        
        return Catch(**created_catch)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create catch: {str(e)}"
        )

@router.get("/{catch_id}", response_model=Catch)
async def get_catch(catch_id: str, viewer_id: Optional[str] = Query(None), db=Depends(get_database)):
    """Get single catch with access control"""
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
            if not viewer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied - login required"
                )
            
            if not ObjectId.is_valid(viewer_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid viewer ID format"
                )
            
            # Check if viewer is following the catch owner
            catch_owner = await db.users.find_one({"_id": catch["user_id"]})
            if catch_owner and ObjectId(viewer_id) not in catch_owner.get("followers", []):
                # Allow if viewer is the owner
                if catch["user_id"] != ObjectId(viewer_id):
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
    viewer_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_database)
):
    """List user's catches with pagination and access control"""
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
        if not viewer_id or user_id != viewer_id:
            if viewer_id and ObjectId.is_valid(viewer_id):
                # Check if viewer is following this user
                is_follower = ObjectId(viewer_id) in user.get("followers", [])
                if is_follower:
                    # Show public catches and those shared with followers
                    query["$or"] = [
                        {"shared_with_followers": {"$ne": True}},
                        {"shared_with_followers": True}
                    ]
                else:
                    # Show only public catches
                    query["shared_with_followers"] = {"$ne": True}
            else:
                # No viewer, show only public catches
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
async def update_catch(catch_id: str, catch_data: CatchUpdate, user_id: str = Query(...), db=Depends(get_database)):
    """Update catch (e.g., description, photo, visibility)"""
    try:
        if not ObjectId.is_valid(catch_id) or not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ID format"
            )
        
        # Check if catch exists and belongs to user
        catch = await db.catches.find_one({"_id": ObjectId(catch_id)})
        if not catch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Catch not found"
            )
        
        if catch["user_id"] != ObjectId(user_id):
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
async def delete_catch(catch_id: str, user_id: str = Query(...), db=Depends(get_database)):
    """Delete a catch"""
    try:
        if not ObjectId.is_valid(catch_id) or not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ID format"
            )
        
        # Check if catch exists and belongs to user
        catch = await db.catches.find_one({"_id": ObjectId(catch_id)})
        if not catch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Catch not found"
            )
        
        if catch["user_id"] != ObjectId(user_id):
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
