from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from bson import ObjectId
import math
from models.schemas import Pin, PinCreate, PinUpdate
from database import get_database
from auth import get_current_user

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points in kilometers using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

router = APIRouter(prefix="/pins", tags=["pins"])

@router.post("/", response_model=Pin, status_code=status.HTTP_201_CREATED)
async def create_pin(
    pin_data: PinCreate, 
    current_user = Depends(get_current_user),  # Require authentication
    db=Depends(get_database)
):
    """Add a catch to the map (requires authentication)"""
    try:
        if not ObjectId.is_valid(str(pin_data.catch_id)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid catch ID format"
            )
        
        # Check if catch exists and belongs to user
        catch = await db.catches.find_one({"_id": ObjectId(str(pin_data.catch_id))})
        if not catch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Catch not found"
            )
        
        # Ensure user can only pin their own catches
        if catch["user_id"] != current_user["_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot pin another user's catch"
            )
        
        # Check if pin already exists for this catch
        existing_pin = await db.pins.find_one({"catch_id": ObjectId(str(pin_data.catch_id))})
        if existing_pin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pin already exists for this catch"
            )
        
        # Create new pin
        pin_dict = pin_data.dict()
        pin_dict["user_id"] = current_user["_id"]  # Use authenticated user's ID
        pin_dict["catch_id"] = ObjectId(str(pin_data.catch_id))
        
        result = await db.pins.insert_one(pin_dict)
        created_pin = await db.pins.find_one({"_id": result.inserted_id})
        
        return Pin(**created_pin)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pin: {str(e)}"
        )

@router.get("/", response_model=List[dict])
async def get_pins(
    current_user = Depends(get_current_user),  # Require authentication
    lat: Optional[float] = Query(None, ge=-90, le=90, description="Center latitude for filtering"),
    lng: Optional[float] = Query(None, ge=-180, le=180, description="Center longitude for filtering"),
    radius: Optional[float] = Query(None, gt=0, description="Radius in kilometers for filtering"),
    db=Depends(get_database)
):
    """Retrieve map pins accessible to the authenticated user"""
    try:
        # Get authenticated user information (required)
        viewer_id = current_user["_id"]
        
        # Build aggregation pipeline for access control
        pipeline = []
        
        # Note: For geospatial queries, we'll need to ensure proper indexing
        # For now, we'll do basic distance filtering in the application layer
        # In production, consider using MongoDB's geospatial indexes and queries
        
        # Lookup user information for access control
        pipeline.extend([
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "_id",
                    "as": "pin_owner"
                }
            },
            {"$unwind": "$pin_owner"},
            {
                "$lookup": {
                    "from": "catches",
                    "localField": "catch_id",
                    "foreignField": "_id",
                    "as": "catch_info"
                }
            },
            {"$unwind": "$catch_info"}
        ])
        
        # Get all pins and filter based on access control
        cursor = db.pins.aggregate(pipeline)
        all_pins = await cursor.to_list(length=None)
        
        accessible_pins = []
        viewer_following = set(current_user.get("following", []))
        
        for pin_data in all_pins:
            pin_owner_id = pin_data["user_id"]
            visibility = pin_data["visibility"]
            
            # Always allow user to see their own pins
            if pin_owner_id == viewer_id:
                accessible = True
            elif visibility == "public":
                accessible = True
            elif visibility == "mutuals":
                # Check if mutual follow (viewer follows owner AND owner follows viewer)
                accessible = (pin_owner_id in viewer_following and 
                            viewer_id in pin_data["pin_owner"].get("followers", []))
            else:  # private
                accessible = False
            
            if accessible:
                # Check catch sharing settings
                catch_info = pin_data["catch_info"]
                if catch_info.get("shared_with_followers", False):
                    # If catch is shared with followers only, check if viewer is a follower or owner
                    if pin_owner_id != viewer_id and viewer_id not in pin_data["pin_owner"].get("followers", []):
                        continue
                
                # Prepare response data
                pin_response = {
                    "id": str(pin_data["_id"]),
                    "user_id": str(pin_data["user_id"]),
                    "catch_id": str(pin_data["catch_id"]),
                    "location": pin_data["location"],
                    "visibility": pin_data["visibility"],
                    "catch_info": {
                        "species": catch_info["species"],
                        "weight": catch_info["weight"],
                        "photo_url": catch_info["photo_url"],
                        "created_at": catch_info["created_at"].isoformat() if "created_at" in catch_info else None
                    },
                    "owner_info": {
                        "username": pin_data["pin_owner"]["username"]
                    }
                }
                
                # Apply distance filtering if coordinates provided
                if lat is not None and lng is not None and radius is not None:
                    pin_lat = pin_data["location"]["lat"]
                    pin_lng = pin_data["location"]["lng"]
                    distance = calculate_distance(lat, lng, pin_lat, pin_lng)
                    if distance <= radius:
                        accessible_pins.append(pin_response)
                else:
                    accessible_pins.append(pin_response)
        
        return accessible_pins
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pins: {str(e)}"
        )

@router.put("/{pin_id}", response_model=Pin)
async def update_pin(
    pin_id: str, 
    pin_data: PinUpdate, 
    current_user = Depends(get_current_user),
    db=Depends(get_database)
):
    """Update pin location or visibility (requires authentication)"""
    try:
        if not ObjectId.is_valid(pin_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid pin ID format"
            )
        
        # Check if pin exists and belongs to user
        pin = await db.pins.find_one({"_id": ObjectId(pin_id)})
        if not pin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pin not found"
            )
        
        if pin["user_id"] != current_user["_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this pin"
            )
        
        # Prepare update data
        update_data = {}
        if pin_data.location is not None:
            update_data["location"] = pin_data.location.dict()
        if pin_data.visibility is not None:
            update_data["visibility"] = pin_data.visibility
        
        if not update_data:
            return Pin(**pin)
        
        # Update pin
        await db.pins.update_one(
            {"_id": ObjectId(pin_id)},
            {"$set": update_data}
        )
        
        updated_pin = await db.pins.find_one({"_id": ObjectId(pin_id)})
        return Pin(**updated_pin)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update pin: {str(e)}"
        )

@router.delete("/{pin_id}")
async def delete_pin(
    pin_id: str, 
    current_user = Depends(get_current_user), 
    db=Depends(get_database)
):
    """Delete a pin (requires authentication)"""
    try:
        if not ObjectId.is_valid(pin_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid pin ID format"
            )
        
        # Check if pin exists and belongs to user
        pin = await db.pins.find_one({"_id": ObjectId(pin_id)})
        if not pin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pin not found"
            )
        
        if pin["user_id"] != current_user["_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this pin"
            )
        
        # Delete pin
        await db.pins.delete_one({"_id": ObjectId(pin_id)})
        
        return {"message": "Pin deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete pin: {str(e)}"
        )
