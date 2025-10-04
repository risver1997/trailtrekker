from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class PrivacyEnum(str, Enum):
    public = "public"
    private = "private"
    friends = "friends"


class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    draft = "draft"

class TripBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    privacy: PrivacyEnum = PrivacyEnum.private
    cover_image_url: Optional[str] = None
    is_active: bool = True
    total_distance: Optional[float] = None
    duration: Optional[int] = None
    status: StatusEnum = StatusEnum.active
    delay: int = 0

class Trip(TripBase):
    trip_id: str
    user_id: str
    created_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class TripCreate(TripBase):
    user_id: str  # foreign key to Users.user_id


class TripUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    privacy: Optional[PrivacyEnum] = None
    cover_image_url: Optional[str] = None
    published_at: Optional[datetime] = None


class TripResponse(BaseModel):
    id: str  # trip_id
    title: str
    description: Optional[str] = None
    created_at: datetime
    ended_at: Optional[date] = None  # end_date
    is_active: bool = True
    total_distance: Optional[float] = 0.0
    duration: Optional[int] = 0
    privacy: PrivacyEnum = PrivacyEnum.private
    cover_image_url: Optional[str] = None
    status: StatusEnum = StatusEnum.active
    delay: int = 0

    class Config:
        orm_mode = True


class TripStatsUpdate(BaseModel):
    total_distance: Optional[float] = None
    duration: Optional[int] = None


class LocationCreate(BaseModel):
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None


class LocationResponse(BaseModel):
    location_id: str
    trip_id: str
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: datetime

    class Config:
        orm_mode = True


class TripEntryCreate(BaseModel):
    title: str
    description: Optional[str] = None
    entry_type: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_urls: Optional[List[str]] = None
    note: Optional[str] = None


class TripEntryResponse(BaseModel):
    id: str  # step_id
    trip_id: str
    title: str
    description: Optional[str] = None
    entry_type: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_urls: Optional[List[str]] = None
    note: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
