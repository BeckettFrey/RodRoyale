# File: services/cloudinary_service.py
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile
from typing import Dict, Optional
import uuid
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class CloudinaryService:
    def __init__(self):
        """Initialize Cloudinary configuration"""
        self._initialized = False
        # Allowed file extensions for images
        self.ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'gif', 'webp', 'heic', 'heif'}
        self.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def _ensure_initialized(self):
        """Ensure Cloudinary is configured (lazy initialization)"""
        if self._initialized:
            return
            
        # Get configuration from environment variables
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY') 
        api_secret = os.getenv('CLOUDINARY_API_SECRET')
        
        if not all([cloud_name, api_key, api_secret]):
            raise ValueError(
                "Cloudinary configuration missing. Please set CLOUDINARY_CLOUD_NAME, "
                "CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET environment variables."
            )
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        
        self._initialized = True
        logger.info("Cloudinary service initialized successfully")
    
    def _allowed_file(self, filename: str) -> bool:
        """Check if the file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    async def upload_image(
        self, 
        file: UploadFile, 
        folder: str = "Rod Royale/catches",
        transformation: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Upload an image to Cloudinary and return the URLs.
        
        Args:
            file: The image file to upload
            folder: Cloudinary folder to organize uploads
            transformation: Optional transformation parameters
            
        Returns:
            Dict containing the URLs of the uploaded image
            
        Raises:
            HTTPException: If file is invalid or upload fails
        """
        self._ensure_initialized()
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not self._allowed_file(file.filename):
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        content = await file.read()
        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {self.MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        try:
            # Generate unique public_id
            public_id = f"{folder}/{uuid.uuid4()}"
            
            # Default transformation for catches (optimize for web)
            default_transformation = {
                'quality': 'auto:good',
                'fetch_format': 'auto',
                'width': 1200,
                'height': 1200,
                'crop': 'limit'
            }
            
            # Merge with custom transformation if provided
            if transformation:
                default_transformation.update(transformation)
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                content,
                public_id=public_id,
                transformation=default_transformation,
                resource_type="image"
            )
            
            logger.info(f"Successfully uploaded image to Cloudinary: {result['public_id']}")
            
            return {
                "url": result['secure_url'],
                "public_id": result['public_id'],
                "original_url": result['secure_url'],
                "thumbnail_url": cloudinary.CloudinaryImage(result['public_id']).build_url(
                    width=300, height=300, crop="fill", quality="auto:good"
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to upload image to Cloudinary: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to upload image: {str(e)}"
            )
    
    def delete_image(self, public_id: str) -> bool:
        """
        Delete an image from Cloudinary.
        
        Args:
            public_id: The public ID of the image to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        self._ensure_initialized()
        
        try:
            result = cloudinary.uploader.destroy(public_id)
            success = result.get('result') == 'ok'
            
            if success:
                logger.info(f"Successfully deleted image from Cloudinary: {public_id}")
            else:
                logger.warning(f"Failed to delete image from Cloudinary: {public_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting image from Cloudinary: {str(e)}")
            return False
    
    def generate_thumbnail_url(self, public_id: str, width: int = 300, height: int = 300) -> str:
        """
        Generate a thumbnail URL for an existing image.
        
        Args:
            public_id: The public ID of the image
            width: Thumbnail width
            height: Thumbnail height
            
        Returns:
            str: The thumbnail URL
        """
        self._ensure_initialized()
        
        return cloudinary.CloudinaryImage(public_id).build_url(
            width=width, 
            height=height, 
            crop="fill", 
            quality="auto:good"
        )
    
    def generate_optimized_url(
        self, 
        public_id: str, 
        width: Optional[int] = None, 
        height: Optional[int] = None
    ) -> str:
        """
        Generate an optimized URL for an existing image.
        
        Args:
            public_id: The public ID of the image
            width: Optional width constraint
            height: Optional height constraint
            
        Returns:
            str: The optimized URL
        """
        self._ensure_initialized()
        
        transformation = {
            'quality': 'auto:good',
            'fetch_format': 'auto'
        }
        
        if width:
            transformation['width'] = width
        if height:
            transformation['height'] = height
        if width or height:
            transformation['crop'] = 'limit'
        
        return cloudinary.CloudinaryImage(public_id).build_url(**transformation)

# Create a singleton instance
cloudinary_service = CloudinaryService()
