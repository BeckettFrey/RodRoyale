# File: routers/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId
import logging

from models.schemas import (
    UserCreate, UserLogin, User, Token, 
    TokenRefresh, AuthResponse, PasswordChange,
    PasswordResetRequest, PasswordReset
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

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """Change user password with current password verification"""
    try:
        logger.info(f"Password change attempt for user: {current_user.get('username', 'unknown')}")
        
        # Verify current password
        try:
            password_verified = AuthUtils.verify_password(password_data.current_password, current_user["password_hash"])
            logger.info(f"Current password verification result: {password_verified}")
        except Exception as e:
            logger.error(f"Error verifying current password: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Password verification error: {str(e)}"
            )
        
        if not password_verified:
            logger.warning(f"Incorrect current password for user: {current_user.get('username', 'unknown')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Check if new password is different from current
        try:
            same_password = AuthUtils.verify_password(password_data.new_password, current_user["password_hash"])
            logger.info(f"New password same as current: {same_password}")
        except Exception as e:
            logger.error(f"Error checking new password: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Password comparison error: {str(e)}"
            )
            
        if same_password:
            logger.warning(f"User tried to use same password: {current_user.get('username', 'unknown')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password"
            )
        
        # Hash new password
        try:
            new_password_hash = AuthUtils.hash_password(password_data.new_password)
            logger.info(f"New password hashed successfully for user: {current_user.get('username', 'unknown')}")
        except Exception as e:
            logger.error(f"Error hashing new password: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Password hashing error: {str(e)}"
            )
        
        # Update password in database
        result = await db.users.update_one(
            {"_id": ObjectId(current_user["_id"])},
            {"$set": {"password_hash": new_password_hash}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )
        
        logger.info(f"Password changed successfully for user {current_user['username']}")
        
        return {
            "message": "Password changed successfully",
            "detail": "Please log in again with your new password"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )

@router.post("/forgot-password")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db = Depends(get_database)
):
    """Request a password reset token"""
    try:
        # Check if user exists
        user = await db.users.find_one({"email": reset_request.email})
        
        if not user:
            # For security, don't reveal if email exists or not
            logger.warning(f"Password reset requested for non-existent email: {reset_request.email}")
            return {
                "message": "If an account with this email exists, a password reset link has been sent",
                "detail": "Check your email for password reset instructions"
            }
        
        # Generate reset token
        reset_token = AuthUtils.create_password_reset_token(reset_request.email)
        
        logger.info(f"Password reset token generated for user: {user['username']}")
        
        # In a real application, you would send this token via email
        # For demo purposes, we'll return it in the response
        # TODO: Integrate with email service (SendGrid, AWS SES, etc.)
        
        return {
            "message": "If an account with this email exists, a password reset link has been sent",
            "detail": "Check your email for password reset instructions",
            "reset_token": reset_token,  # Remove this in production!
            "note": "In production, this token would be sent via email, not returned in the API response"
        }
        
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db = Depends(get_database)
):
    """Reset password using a valid reset token"""
    try:
        # Verify the reset token
        email = AuthUtils.verify_password_reset_token(reset_data.token)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Find user by email
        user = await db.users.find_one({"email": email})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        # Hash the new password
        new_password_hash = AuthUtils.hash_password(reset_data.new_password)
        
        # Update password in database
        result = await db.users.update_one(
            {"_id": ObjectId(user["_id"])},
            {"$set": {"password_hash": new_password_hash}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password"
            )
        
        logger.info(f"Password reset successfully for user: {user['username']}")
        
        return {
            "message": "Password reset successfully",
            "detail": "You can now log in with your new password"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )
