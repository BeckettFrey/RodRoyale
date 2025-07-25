from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId
import logging

from models.schemas import (
    UserCreate, UserLogin, User, Token, TokenRefresh, 
    AuthResponse
)
from database import get_database
from auth import AuthUtils, get_current_user

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db=Depends(get_database)):
    """Register a new user and return authentication tokens"""
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
        
        # Hash password and create user
        user_dict = user_data.dict()
        user_dict["password_hash"] = AuthUtils.hash_password(user_dict.pop("password"))
        user_dict["followers"] = []
        user_dict["following"] = []
        user_dict["created_at"] = user_dict.get("created_at", None)
        
        result = await db.users.insert_one(user_dict)
        created_user = await db.users.find_one({"_id": result.inserted_id})
        
        # Remove password hash from response
        user_response = {k: v for k, v in created_user.items() if k != "password_hash"}
        
        # Create tokens
        access_token = AuthUtils.create_access_token(data={"sub": str(created_user["_id"])})
        refresh_token = AuthUtils.create_refresh_token(data={"sub": str(created_user["_id"])})
        
        return AuthResponse(
            user=User(**user_response),
            token=Token(
                access_token=access_token,
                refresh_token=refresh_token
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )

@router.post("/login", response_model=AuthResponse)
async def login(login_data: UserLogin, db=Depends(get_database)):
    """Authenticate user and return tokens"""
    try:
        # Find user by email
        user = await db.users.find_one({"email": login_data.email})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not AuthUtils.verify_password(login_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Remove password hash from response
        user_response = {k: v for k, v in user.items() if k != "password_hash"}
        
        # Create tokens
        access_token = AuthUtils.create_access_token(data={"sub": str(user["_id"])})
        refresh_token = AuthUtils.create_refresh_token(data={"sub": str(user["_id"])})
        
        return AuthResponse(
            user=User(**user_response),
            token=Token(
                access_token=access_token,
                refresh_token=refresh_token
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, db=Depends(get_database)):
    """Refresh access token using refresh token"""
    try:
        # Decode refresh token
        payload = AuthUtils.decode_token(token_data.refresh_token)
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user exists
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new tokens
        access_token = AuthUtils.create_access_token(data={"sub": user_id})
        refresh_token = AuthUtils.create_refresh_token(data={"sub": user_id})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )

@router.get("/me", response_model=User)
async def get_current_user_profile(current_user = Depends(get_current_user)):
    """Get current authenticated user's profile"""
    # Remove password hash from response
    user_response = {k: v for k, v in current_user.items() if k != "password_hash"}
    return User(**user_response)

@router.post("/logout")
async def logout():
    """Logout user (client should delete tokens)"""
    return {"message": "Successfully logged out. Please delete your tokens on the client side."}
