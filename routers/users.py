from fastapi import APIRouter, HTTPException, Depends, status, Query
from bson import ObjectId
from typing import List
from models.schemas import User, UserCreate, UserUpdate, PublicUser
from database import get_database
from auth import AuthUtils, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db=Depends(get_database)):
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({
            "$or": [
                {"email": user_data.email},
                {"username": user_data.username}
            ]
        })
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
        
        # Create new user with hashed password
        user_dict = user_data.dict()
        user_dict["password_hash"] = AuthUtils.hash_password(user_dict.pop("password"))
        user_dict["followers"] = []
        user_dict["following"] = []
        
        result = await db.users.insert_one(user_dict)
        created_user = await db.users.find_one({"_id": result.inserted_id})
        
        # Remove password hash from response
        user_response = {k: v for k, v in created_user.items() if k != "password_hash"}
        
        return User(**user_response)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.get("/search", response_model=List[PublicUser])
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db=Depends(get_database)
):
    """Search users by username or bio"""
    try:
        # Create case-insensitive regex search
        search_pattern = {"$regex": q, "$options": "i"}
        
        # Search in username and bio fields
        query = {
            "$or": [
                {"username": search_pattern},
                {"bio": search_pattern}
            ]
        }
        
        cursor = db.users.find(query).limit(limit)
        users = await cursor.to_list(length=limit)
        
        # Remove password hashes and emails from response
        user_results = []
        for user in users:
            user_response = {k: v for k, v in user.items() if k not in ["password_hash", "email"]}
            user_results.append(PublicUser(**user_response))
        
        return user_results
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search users: {str(e)}"
        )

@router.get("/{user_id}", response_model=PublicUser)
async def get_user(user_id: str, db=Depends(get_database)):
    """Get user profile by ID"""
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Remove password hash and email from response
        user_response = {k: v for k, v in user.items() if k not in ["password_hash", "email"]}
        
        return PublicUser(**user_response)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )

@router.get("/me", response_model=User)
async def get_current_user_profile(current_user = Depends(get_current_user), db=Depends(get_database)):
    """Get current user's own profile (includes email)"""
    try:
        user_id = current_user["_id"]
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
            
        user = await db.users.find_one({"_id": user_id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Remove password hash but keep email for own profile
        user_response = {k: v for k, v in user.items() if k != "password_hash"}
        
        return User(**user_response)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str, 
    user_data: UserUpdate, 
    current_user = Depends(get_current_user),  # Require authentication
    db=Depends(get_database)
):
    """Update user profile (requires authentication)"""
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Ensure user can only update their own profile
        if str(current_user["_id"]) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own profile"
            )
        
        # Prepare update data
        update_data = {k: v for k, v in user_data.dict().items() if v is not None}
        
        if not update_data:
            user_response = {k: v for k, v in current_user.items() if k != "password_hash"}
            return User(**user_response)
        
        # Handle password update
        if "password" in update_data:
            update_data["password_hash"] = AuthUtils.hash_password(update_data.pop("password"))
        
        # Check for duplicate email/username if being updated
        if "email" in update_data or "username" in update_data:
            duplicate_check = {}
            if "email" in update_data:
                duplicate_check["email"] = update_data["email"]
            if "username" in update_data:
                duplicate_check["username"] = update_data["username"]
            
            duplicate_user = await db.users.find_one({
                "$and": [
                    {"_id": {"$ne": ObjectId(user_id)}},
                    {"$or": [duplicate_check]}
                ]
            })
            
            if duplicate_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email or username already taken"
                )
        
        # Update user
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
        # Remove password hash from response
        user_response = {k: v for k, v in updated_user.items() if k != "password_hash"}
        return User(**user_response)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.post("/{user_id}/follow/{target_user_id}")
async def follow_user(user_id: str, target_user_id: str, db=Depends(get_database)):
    """Follow another user"""
    try:
        if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(target_user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        if user_id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot follow yourself"
            )
        
        # Check if both users exist
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        target_user = await db.users.find_one({"_id": ObjectId(target_user_id)})
        
        if not user or not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Add to following list
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"following": ObjectId(target_user_id)}}
        )
        
        # Add to followers list
        await db.users.update_one(
            {"_id": ObjectId(target_user_id)},
            {"$addToSet": {"followers": ObjectId(user_id)}}
        )
        
        return {"message": "Successfully followed user"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to follow user: {str(e)}"
        )

@router.delete("/{user_id}/follow/{target_user_id}")
async def unfollow_user(user_id: str, target_user_id: str, db=Depends(get_database)):
    """Unfollow another user"""
    try:
        if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(target_user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Remove from following list
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"following": ObjectId(target_user_id)}}
        )
        
        # Remove from followers list
        await db.users.update_one(
            {"_id": ObjectId(target_user_id)},
            {"$pull": {"followers": ObjectId(user_id)}}
        )
        
        return {"message": "Successfully unfollowed user"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unfollow user: {str(e)}"
        )

@router.get("/{user_id}/followers", response_model=List[PublicUser])
async def get_user_followers(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db=Depends(get_database)
):
    """Get a user's followers"""
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Get user and their followers
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        follower_ids = user.get("followers", [])
        if not follower_ids:
            return []
        
        # Get follower details with pagination
        cursor = db.users.find(
            {"_id": {"$in": follower_ids}}
        ).skip(skip).limit(limit)
        
        followers = await cursor.to_list(length=limit)
        
        # Remove password hashes and emails
        follower_results = []
        for follower in followers:
            follower_response = {k: v for k, v in follower.items() if k not in ["password_hash", "email"]}
            follower_results.append(PublicUser(**follower_response))
        
        return follower_results
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get followers: {str(e)}"
        )

@router.get("/{user_id}/following", response_model=List[PublicUser])
async def get_user_following(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db=Depends(get_database)
):
    """Get users that a user is following"""
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Get user and who they're following
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        following_ids = user.get("following", [])
        if not following_ids:
            return []
        
        # Get following details with pagination
        cursor = db.users.find(
            {"_id": {"$in": following_ids}}
        ).skip(skip).limit(limit)
        
        following = await cursor.to_list(length=limit)
        
        # Remove password hashes and emails
        following_results = []
        for followed_user in following:
            user_response = {k: v for k, v in followed_user.items() if k not in ["password_hash", "email"]}
            following_results.append(PublicUser(**user_response))
        
        return following_results
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get following: {str(e)}"
        )

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
    current_user = Depends(get_current_user),  # Require authentication
    db=Depends(get_database)
):
    """Delete current user's account and all associated data"""
    try:
        user_id = current_user["_id"]
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        
        # Step 1: Get user data before deletion
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Step 2: Remove user from followers' following lists
        followers = user.get("followers", [])
        if followers:
            await db.users.update_many(
                {"_id": {"$in": followers}},
                {"$pull": {"following": user_id}}
            )
        
        # Step 3: Remove user from following users' followers lists
        following = user.get("following", [])
        if following:
            await db.users.update_many(
                {"_id": {"$in": following}},
                {"$pull": {"followers": user_id}}
            )
        
        # Step 4: Delete all user's catches
        catches_result = await db.catches.delete_many({"user_id": user_id})
        
        # Step 5: Delete all user's pins
        pins_result = await db.pins.delete_many({"user_id": user_id})
        
        # Step 6: Delete the user account
        user_result = await db.users.delete_one({"_id": user_id})
        
        if user_result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user account"
            )
        
        # Log the deletion results (optional)
        deletion_summary = {
            "user_deleted": user_result.deleted_count,
            "catches_deleted": catches_result.deleted_count,
            "pins_deleted": pins_result.deleted_count,
            "followers_updated": len(followers),
            "following_updated": len(following)
        }
        
        # Return nothing (204 No Content)
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )
