# File: routers/uploads.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
import logging
from typing import Dict, Optional
from services.cloudinary_service import cloudinary_service
from models.schemas import ThumbnailResponse, OptimizedResponse

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/upload",
    tags=["uploads"]
)

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    folder: Optional[str] = Query("Rod Royale/catches", description="Cloudinary folder to organize uploads")
) -> Dict[str, str]:
    """
    Upload an image file to Cloudinary and return the URLs where it can be accessed.
    
    Args:
        file: The image file to upload
        folder: Cloudinary folder to organize uploads (default: Rod Royale/catches)
        
    Returns:
        Dict containing the URLs of the uploaded image
        
    Raises:
        HTTPException: If file is invalid or upload fails
    """
    try:
        result = await cloudinary_service.upload_image(file, folder)
        logger.info(f"Successfully uploaded image: {result['public_id']}")
        return result
        
    except HTTPException:
        # Re-raise HTTPExceptions from the service
        raise
    except Exception as e:
        logger.error(f"Unexpected error during image upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload image")

@router.delete("/image/{public_id:path}")
async def delete_image(public_id: str) -> Dict[str, str]:
    """
    Delete an image from Cloudinary.
    
    Args:
        public_id: The public ID of the image to delete (from upload response)
        
    Returns:
        Dict with success status
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        success = cloudinary_service.delete_image(public_id)
        
        if success:
            logger.info(f"Successfully deleted image: {public_id}")
            return {"message": "Image deleted successfully", "public_id": public_id}
        else:
            raise HTTPException(
                status_code=404, 
                detail="Image not found or could not be deleted"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during image deletion: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete image")

@router.get("/image/{public_id:path}/thumbnail")
async def get_thumbnail_url(
    public_id: str,
    width: int = Query(300, ge=50, le=1000, description="Thumbnail width"),
    height: int = Query(300, ge=50, le=1000, description="Thumbnail height")
) -> ThumbnailResponse:
    """
    Generate a thumbnail URL for an existing image.
    
    Args:
        public_id: The public ID of the image
        width: Thumbnail width (50-1000px)
        height: Thumbnail height (50-1000px)
        
    Returns:
        Dict containing the thumbnail URL
    """
    try:
        thumbnail_url = cloudinary_service.generate_thumbnail_url(public_id, width, height)
        return ThumbnailResponse(
            thumbnail_url=thumbnail_url,
            public_id=public_id,
            width=width,
            height=height
        )
        
    except Exception as e:
        logger.error(f"Error generating thumbnail URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate thumbnail URL")

@router.get("/image/{public_id:path}/optimized")
async def get_optimized_url(
    public_id: str,
    width: Optional[int] = Query(None, ge=50, le=2000, description="Max width"),
    height: Optional[int] = Query(None, ge=50, le=2000, description="Max height")
) -> OptimizedResponse:
    """
    Generate an optimized URL for an existing image.
    
    Args:
        public_id: The public ID of the image
        width: Optional max width (50-2000px)
        height: Optional max height (50-2000px)
        
    Returns:
        Dict containing the optimized URL
    """
    try:
        optimized_url = cloudinary_service.generate_optimized_url(public_id, width, height)
        return OptimizedResponse(
            optimized_url=optimized_url,
            public_id=public_id,
            width=width,
            height=height
        )
        
    except Exception as e:
        logger.error(f"Error generating optimized URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate optimized URL")
