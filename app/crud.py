import uuid
from sqlalchemy.orm import Session
import models, schemas
from typing import Dict, Any
from datetime import date
from models import StatusEnum


def create_trip(db: Session, trip: schemas.TripCreate):
    db_trip = models.Trip(
        trip_id=str(uuid.uuid4()),
        user_id=trip.user_id,
        title=trip.title,
        description=trip.description,
        start_date=trip.start_date,
        end_date=trip.end_date,
        privacy=trip.privacy,
        cover_image_url=trip.cover_image_url,
        is_active=trip.is_active,
        total_distance=trip.total_distance or 0.0,
        duration=trip.duration or 0,
        status=trip.status,
        delay=trip.delay,
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip


def get_trip(db: Session, trip_id: str):
    return db.query(models.Trip).filter(models.Trip.trip_id == trip_id).first()


def get_trips_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Trip)
        .filter(models.Trip.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all_trips(db: Session, skip: int = 0, limit: int = 100):
    """Get all trips with pagination"""
    return (
        db.query(models.Trip)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_trip(db: Session, trip_id: str, trip: schemas.TripUpdate):
    db_trip = db.query(models.Trip).filter(models.Trip.trip_id == trip_id).first()
    if not db_trip:
        return None
    for key, value in trip.dict(exclude_unset=True).items():
        setattr(db_trip, key, value)
    db.commit()
    db.refresh(db_trip)
    return db_trip


def delete_trip(db: Session, trip_id: str):
    db_trip = db.query(models.Trip).filter(models.Trip.trip_id == trip_id).first()
    if db_trip:
        db.delete(db_trip)
        db.commit()
    return db_trip

def get_active_trip(db: Session, user_id: str):
    """Get the active trip for a user (most recent trip with is_active=True and status='active')"""
    return (
        db.query(models.Trip)
        .filter(
            models.Trip.user_id == user_id,
            models.Trip.is_active == True,
            models.Trip.status == models.StatusEnum.active
        )
        .order_by(models.Trip.created_at.desc())
        .first()
    )


def end_trip(db: Session, trip_id: str):
    """End a trip by setting status to completed, is_active to false, and end_date to current date"""
    
    db_trip = db.query(models.Trip).filter(models.Trip.trip_id == trip_id).first()
    if not db_trip:
        return None
    
    # Update trip to ended state
    db_trip.is_active = False
    db_trip.status = StatusEnum.completed
    db_trip.end_date = date.today()
    
    db.commit()
    db.refresh(db_trip)
    return db_trip


def update_trip_stats(db: Session, trip_id: str, stats: schemas.TripStatsUpdate):
    """Update trip statistics (total_distance and duration)"""
    db_trip = db.query(models.Trip).filter(models.Trip.trip_id == trip_id).first()
    if not db_trip:
        return None
    
    # Update only the provided stats
    if stats.total_distance is not None:
        db_trip.total_distance = stats.total_distance
    if stats.duration is not None:
        db_trip.duration = stats.duration
    
    db.commit()
    db.refresh(db_trip)
    return db_trip


def create_location(db: Session, trip_id: str, location: schemas.LocationCreate):
    """Create a new location for a trip"""
    db_location = models.Location(
        location_id=str(uuid.uuid4()),
        trip_id=trip_id,
        latitude=location.latitude,
        longitude=location.longitude,
        altitude=location.altitude,
        accuracy=location.accuracy,
        speed=location.speed,
        heading=location.heading,
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def get_locations_by_trip(db: Session, trip_id: str, skip: int = 0, limit: int = 100):
    """Get all locations for a trip with pagination"""
    return (
        db.query(models.Location)
        .filter(models.Location.trip_id == trip_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_last_location_by_trip(db: Session, trip_id: str):
    """Get the last (most recent) location for a trip"""
    return (
        db.query(models.Location)
        .filter(models.Location.trip_id == trip_id)
        .order_by(models.Location.timestamp.desc())
        .first()
    )


def create_trip_entry(db: Session, trip_id: str, entry: schemas.TripEntryCreate):
    """Create a new trip entry"""
    db_entry = models.TripEntry(
        step_id=str(uuid.uuid4()),
        trip_id=trip_id,
        title=entry.title,
        description=entry.description,
        entry_type=entry.entry_type,
        location_name=entry.location_name,
        latitude=entry.latitude,
        longitude=entry.longitude,
        image_urls=entry.image_urls,
        note=entry.note,
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_trip_entries_by_trip(db: Session, trip_id: str, skip: int = 0, limit: int = 100):
    """Get all trip entries for a trip with pagination"""
    return (
        db.query(models.TripEntry)
        .filter(models.TripEntry.trip_id == trip_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def map_trip_to_response(db_trip: models.Trip) -> Dict[str, Any]:
    """Map database trip model to API response format"""
    return {
        "id": db_trip.trip_id,
        "title": db_trip.title,
        "description": db_trip.description,
        "created_at": db_trip.created_at,
        "ended_at": db_trip.end_date,
        "is_active": db_trip.is_active,
        "total_distance": db_trip.total_distance or 0.0,
        "duration": db_trip.duration or 0,
        "privacy": db_trip.privacy,
        "cover_image_url": db_trip.cover_image_url,
        "status": db_trip.status,
        "delay": db_trip.delay,
    }