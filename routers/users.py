from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId
from models.schemas import User, UserCreate, UserUpdate
from database import get_database

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
        
        # Create new user
        user_dict = user_data.dict()
        user_dict["followers"] = []
        user_dict["following"] = []
        
        result = await db.users.insert_one(user_dict)
        created_user = await db.users.find_one({"_id": result.inserted_id})
        
        return User(**created_user)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.get("/{user_id}", response_model=User)
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
        
        return User(**user)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user_data: UserUpdate, db=Depends(get_database)):
    """Update user profile or following"""
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Check if user exists
        existing_user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prepare update data
        update_data = {k: v for k, v in user_data.dict().items() if v is not None}
        
        if not update_data:
            return User(**existing_user)
        
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
        return User(**updated_user)
    
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
