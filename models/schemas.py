from pydantic import BaseModel, Field, EmailStr, ConfigDict
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from pydantic import GetJsonSchemaHandler
from typing import Optional, List, Any
from bson import ObjectId
from datetime import datetime

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string", "format": "objectid"}

    def __str__(self):
        return str(super())

class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")

# User Models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    bio: Optional[str] = Field(None, max_length=500)

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    bio: Optional[str] = Field(None, max_length=500)

class User(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    followers: List[PyObjectId] = Field(default_factory=list)
    following: List[PyObjectId] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Catch Models
class CatchBase(BaseModel):
    species: str = Field(..., min_length=1, max_length=100)
    weight: float = Field(..., gt=0)
    photo_url: str = Field(..., pattern=r'^https?://.+')
    location: Location
    shared_with_followers: bool = False

class CatchCreate(CatchBase):
    pass

class CatchUpdate(BaseModel):
    species: Optional[str] = Field(None, min_length=1, max_length=100)
    weight: Optional[float] = Field(None, gt=0)
    photo_url: Optional[str] = Field(None, pattern=r'^https?://.+')
    location: Optional[Location] = None
    shared_with_followers: Optional[bool] = None

class Catch(CatchBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str, datetime: lambda v: v.isoformat()}
    )

# Pin Models
class PinBase(BaseModel):
    catch_id: PyObjectId
    location: Location
    visibility: str = Field(..., pattern=r'^(private|mutuals|public)$')

class PinCreate(PinBase):
    pass

class PinUpdate(BaseModel):
    location: Optional[Location] = None
    visibility: Optional[str] = Field(None, pattern=r'^(private|mutuals|public)$')

class Pin(PinBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )