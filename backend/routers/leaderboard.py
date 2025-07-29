# File: routers/leaderboard.py
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, Any
from bson import ObjectId
from datetime import datetime, timedelta
from database import get_database
from auth import get_current_user

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

@router.get("/my-stats", response_model=Dict[str, Any])
async def get_my_leaderboard_stats(
    current_user = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get current user's leaderboard statistics"""
    try:
        user_id = current_user["_id"]
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        
        # Get all user's catches
        user_catches = await db.catches.find({"user_id": user_id}).to_list(length=None)
        
        # Calculate metrics for this month
        month_ago = datetime.utcnow() - timedelta(days=30)
        month_catches = [c for c in user_catches if c.get('created_at', datetime.min) >= month_ago]
        
        stats = {
            "user_id": str(user_id),
            "username": current_user.get("username", "Unknown"),
            "total_catches": len(user_catches),
            "biggest_catch_month": 0.0,
            "biggest_catch_species": None,
            "catches_this_month": len(month_catches),
            "best_average_month": 0.0,
            "all_time_weight": 0.0
        }
        
        if month_catches:
            # Calculate biggest catch this month
            biggest = max(month_catches, key=lambda x: x.get('weight', 0))
            stats["biggest_catch_month"] = biggest.get('weight', 0)
            stats["biggest_catch_species"] = biggest.get('species', 'Unknown')
            
            # Calculate best average this month
            total_weight = sum(c.get('weight', 0) for c in month_catches)
            stats["best_average_month"] = round(total_weight / len(month_catches), 2)
        
        if user_catches:
            # Calculate all-time total weight
            total_weight = sum(c.get('weight', 0) for c in user_catches)
            stats["all_time_weight"] = round(total_weight, 2)
        
        return stats
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get leaderboard stats: {str(e)}"
        )

@router.get("/following-comparison", response_model=Dict[str, Any])
async def get_following_leaderboard(
    current_user = Depends(get_current_user),
    metric: str = Query("biggest_catch_month", regex="^(biggest_catch_month|catches_this_month|best_average_month)$"),
    limit: int = Query(10, ge=1, le=50),
    db=Depends(get_database)
):
    """Get leaderboard comparing current user with users they follow"""
    try:
        user_id = current_user["_id"]
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        
        # Get current user's following list
        user_profile = await db.users.find_one({"_id": user_id})
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Create list of user IDs to compare (user + following)
        comparison_user_ids = [user_id]
        following_list = user_profile.get("following", [])
        for followed_user_id in following_list:
            if isinstance(followed_user_id, str):
                followed_user_id = ObjectId(followed_user_id)
            comparison_user_ids.append(followed_user_id)
        
        # Get all users in comparison
        users = await db.users.find({"_id": {"$in": comparison_user_ids}}).to_list(length=None)
        user_lookup = {str(u["_id"]): u for u in users}
        
        # Calculate stats for each user
        leaderboard = []
        month_ago = datetime.utcnow() - timedelta(days=30)
        
        for comp_user_id in comparison_user_ids:
            user_catches = await db.catches.find({"user_id": comp_user_id}).to_list(length=None)
            user_info = user_lookup.get(str(comp_user_id), {})
            
            # Filter catches for this month
            month_catches = [c for c in user_catches if c.get('created_at', datetime.min) >= month_ago]
            
            stats = {
                "user_id": str(comp_user_id),
                "username": user_info.get("username", "Unknown"),
                "bio": user_info.get("bio", ""),
                "is_current_user": comp_user_id == user_id,
                "total_catches": len(user_catches),
                "biggest_catch_month": 0.0,
                "biggest_catch_species": None,
                "catches_this_month": len(month_catches),
                "best_average_month": 0.0
            }
            
            if month_catches:
                # Calculate biggest catch this month
                biggest = max(month_catches, key=lambda x: x.get('weight', 0))
                stats["biggest_catch_month"] = biggest.get('weight', 0)
                stats["biggest_catch_species"] = biggest.get('species', 'Unknown')
                
                # Calculate best average this month
                total_weight = sum(c.get('weight', 0) for c in month_catches)
                stats["best_average_month"] = round(total_weight / len(month_catches), 2)
            
            leaderboard.append(stats)
        
        # Sort by requested metric
        if metric == "biggest_catch_month":
            leaderboard.sort(key=lambda x: x["biggest_catch_month"], reverse=True)
        elif metric == "catches_this_month":
            leaderboard.sort(key=lambda x: x["catches_this_month"], reverse=True)
        elif metric == "best_average_month":
            leaderboard.sort(key=lambda x: x["best_average_month"], reverse=True)
        
        # Add ranking
        for i, user_stats in enumerate(leaderboard):
            user_stats["rank"] = i + 1
        
        # Limit results
        leaderboard = leaderboard[:limit]
        
        # Find current user's position
        current_user_rank = None
        current_user_stats = None
        for user_stats in leaderboard:
            if user_stats["is_current_user"]:
                current_user_rank = user_stats["rank"]
                current_user_stats = user_stats
                break
        
        return {
            "metric": metric,
            "total_users": len(comparison_user_ids),
            "current_user_rank": current_user_rank,
            "current_user_stats": current_user_stats,
            "leaderboard": leaderboard
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get following leaderboard: {str(e)}"
        )

@router.get("/global", response_model=Dict[str, Any])
async def get_global_leaderboard(
    metric: str = Query("biggest_catch_month", regex="^(biggest_catch_month|catches_this_month|best_average_month)$"),
    limit: int = Query(10, ge=1, le=50),
    current_user = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get global leaderboard for all users"""
    try:
        user_id = current_user["_id"]
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        
        # Get all users
        all_users = await db.users.find({}).to_list(length=None)
        
        # Calculate stats for each user
        leaderboard = []
        month_ago = datetime.utcnow() - timedelta(days=30)
        
        for user in all_users:
            user_catches = await db.catches.find({"user_id": user["_id"]}).to_list(length=None)
            
            # Filter catches for this month
            month_catches = [c for c in user_catches if c.get('created_at', datetime.min) >= month_ago]
            
            stats = {
                "user_id": str(user["_id"]),
                "username": user.get("username", "Unknown"),
                "bio": user.get("bio", ""),
                "is_current_user": user["_id"] == user_id,
                "total_catches": len(user_catches),
                "biggest_catch_month": 0.0,
                "biggest_catch_species": None,
                "catches_this_month": len(month_catches),
                "best_average_month": 0.0
            }
            
            if month_catches:
                # Calculate biggest catch this month
                biggest = max(month_catches, key=lambda x: x.get('weight', 0))
                stats["biggest_catch_month"] = biggest.get('weight', 0)
                stats["biggest_catch_species"] = biggest.get('species', 'Unknown')
                
                # Calculate best average this month
                total_weight = sum(c.get('weight', 0) for c in month_catches)
                stats["best_average_month"] = round(total_weight / len(month_catches), 2)
            
            # Only include users with at least one catch this month
            if stats["catches_this_month"] > 0:
                leaderboard.append(stats)
        
        # Sort by requested metric
        if metric == "biggest_catch_month":
            leaderboard.sort(key=lambda x: x["biggest_catch_month"], reverse=True)
        elif metric == "catches_this_month":
            leaderboard.sort(key=lambda x: x["catches_this_month"], reverse=True)
        elif metric == "best_average_month":
            leaderboard.sort(key=lambda x: x["best_average_month"], reverse=True)
        
        # Add ranking
        for i, user_stats in enumerate(leaderboard):
            user_stats["rank"] = i + 1
        
        # Find current user's position in full leaderboard
        current_user_rank = None
        current_user_stats = None
        for user_stats in leaderboard:
            if user_stats["is_current_user"]:
                current_user_rank = user_stats["rank"]
                current_user_stats = user_stats
                break
        
        # Limit results for response
        top_leaderboard = leaderboard[:limit]
        
        return {
            "metric": metric,
            "total_users": len(leaderboard),
            "current_user_rank": current_user_rank,
            "current_user_stats": current_user_stats,
            "leaderboard": top_leaderboard
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get global leaderboard: {str(e)}"
        )

@router.get("/species/{species}", response_model=Dict[str, Any])
async def get_species_leaderboard(
    species: str,
    metric: str = Query("biggest_catch_month", regex="^(biggest_catch_month|catches_this_month|best_average_month)$"),
    limit: int = Query(10, ge=1, le=50),
    current_user = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get leaderboard for a specific fish species"""
    try:
        user_id = current_user["_id"]
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        
        # Get all catches for this species in the last month
        month_ago = datetime.utcnow() - timedelta(days=30)
        species_catches = await db.catches.find({
            "species": {"$regex": species, "$options": "i"},
            "created_at": {"$gte": month_ago}
        }).to_list(length=None)
        
        # Group catches by user
        user_catches_map = {}
        for catch in species_catches:
            user_catch_id = catch["user_id"]
            if user_catch_id not in user_catches_map:
                user_catches_map[user_catch_id] = []
            user_catches_map[user_catch_id].append(catch)
        
        # Get user information
        user_ids = list(user_catches_map.keys())
        users = await db.users.find({"_id": {"$in": user_ids}}).to_list(length=None)
        user_lookup = {u["_id"]: u for u in users}
        
        # Calculate stats for each user
        leaderboard = []
        
        for user_catch_id, catches in user_catches_map.items():
            user_info = user_lookup.get(user_catch_id, {})
            
            stats = {
                "user_id": str(user_catch_id),
                "username": user_info.get("username", "Unknown"),
                "bio": user_info.get("bio", ""),
                "is_current_user": user_catch_id == user_id,
                "total_catches": len(catches),
                "biggest_catch_month": 0.0,
                "catches_this_month": len(catches),
                "best_average_month": 0.0
            }
            
            # Calculate biggest catch for this species this month
            biggest = max(catches, key=lambda x: x.get('weight', 0))
            stats["biggest_catch_month"] = biggest.get('weight', 0)
            
            # Calculate best average for this species this month
            total_weight = sum(c.get('weight', 0) for c in catches)
            stats["best_average_month"] = round(total_weight / len(catches), 2)
            
            leaderboard.append(stats)
        
        # Sort by requested metric
        if metric == "biggest_catch_month":
            leaderboard.sort(key=lambda x: x["biggest_catch_month"], reverse=True)
        elif metric == "catches_this_month":
            leaderboard.sort(key=lambda x: x["catches_this_month"], reverse=True)
        elif metric == "best_average_month":
            leaderboard.sort(key=lambda x: x["best_average_month"], reverse=True)
        
        # Add ranking
        for i, user_stats in enumerate(leaderboard):
            user_stats["rank"] = i + 1
        
        # Find current user's position
        current_user_rank = None
        current_user_stats = None
        for user_stats in leaderboard:
            if user_stats["is_current_user"]:
                current_user_rank = user_stats["rank"]
                current_user_stats = user_stats
                break
        
        # Limit results
        top_leaderboard = leaderboard[:limit]
        
        return {
            "species": species,
            "metric": metric,
            "total_users": len(leaderboard),
            "current_user_rank": current_user_rank,
            "current_user_stats": current_user_stats,
            "leaderboard": top_leaderboard
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get species leaderboard: {str(e)}"
        )
