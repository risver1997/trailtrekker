from sqlalchemy.orm import relationship
from config import USERS_TABLE, TRIPS_TABLE, LOCATIONS_TABLE, TRIP_ENTRIES_TABLE
from sqlalchemy import Column, String, Text, Date, Enum, Float, Integer, TIMESTAMP, ForeignKey, Boolean, Double, JSON
from sqlalchemy.sql import func
from database import Base
import enum


class PrivacyEnum(str, enum.Enum):
    public = "public"
    private = "private"
    friends = "friends"


class StatusEnum(str, enum.Enum):
    active = "active"
    inactive = "completed"
    draft = "draft"

class User(Base):
    __tablename__ = USERS_TABLE

    user_id = Column(String(36), primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    profile_picture_url = Column(String(512))
    bio = Column(Text)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    trips = relationship("Trip", back_populates="owner")


class Trip(Base):
    __tablename__ = TRIPS_TABLE

    trip_id = Column(String(36), primary_key=True, index=True)  # UUID
    user_id = Column(String(36), ForeignKey("Users.user_id"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    # updated fields
    privacy = Column(Enum(PrivacyEnum), nullable=False, default=PrivacyEnum.private)
    cover_image_url = Column(String(512))

    is_active = Column(Boolean, nullable=False, default=True)
    total_distance = Column(Float, nullable=True)
    duration = Column(Integer, nullable=True)  # seconds
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.active)
    delay = Column(Integer, nullable=False, default=0)

    created_at = Column(TIMESTAMP, server_default=func.now())
    published_at = Column(TIMESTAMP, nullable=True)

    # Relationship to locations
    locations = relationship("Location", back_populates="trip")
    
    # Relationship to trip entries
    entries = relationship("TripEntry", back_populates="trip")


class Location(Base):
    __tablename__ = LOCATIONS_TABLE

    location_id = Column(String(36), primary_key=True, index=True)  # UUID
    trip_id = Column(String(36), ForeignKey("trips.trip_id"), nullable=False)

    latitude = Column(Double, nullable=False)
    longitude = Column(Double, nullable=False)
    altitude = Column(Double, nullable=True)
    accuracy = Column(Double, nullable=True)
    speed = Column(Double, nullable=True)
    heading = Column(Double, nullable=True)

    timestamp = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationship back to trip
    trip = relationship("Trip", back_populates="locations")


class TripEntry(Base):
    __tablename__ = TRIP_ENTRIES_TABLE

    step_id = Column(String(36), primary_key=True, index=True)  # UUID
    trip_id = Column(String(36), ForeignKey("trips.trip_id"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    entry_type = Column(String(100), nullable=True)

    location_name = Column(String(255), nullable=True)
    latitude = Column(Double, nullable=True)
    longitude = Column(Double, nullable=True)

    image_urls = Column(JSON, nullable=True)  # JSON array of strings
    note = Column(Text, nullable=True)

    timestamp = Column(TIMESTAMP, nullable=False, server_default=func.now())
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationship back to trip
    trip = relationship("Trip", back_populates="entries")
