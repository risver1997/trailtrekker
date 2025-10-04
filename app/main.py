from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import crud, schemas, models
from database import engine, Base, get_db
from typing import List
from datetime import datetime

# Create tables at startup (for dev/demo; in prod use Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TrailTrekker App API", version="1.0.0")

@app.post("/api/trips")
def create_trip(trip: schemas.TripCreate, db: Session = Depends(get_db)):
    db_trip = crud.create_trip(db=db, trip=trip)
    return crud.map_trip_to_response(db_trip)

@app.get("/api/trips")
def get_all_trips(skip: int = Query(0, ge=0, description="Number of trips to skip"), 
                  limit: int = Query(100, ge=1, le=1000, description="Maximum number of trips to return"), 
                  db: Session = Depends(get_db)):
    """Get all trips with pagination"""
    trips = crud.get_all_trips(db, skip=skip, limit=limit)
    return [crud.map_trip_to_response(trip) for trip in trips]

@app.get("/api/trips/{trip_id}")
def read_trip(trip_id: str, db: Session = Depends(get_db)):
    db_trip = crud.get_trip(db, trip_id=trip_id)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return crud.map_trip_to_response(db_trip)


@app.get("/api/trips/active")
def get_active_trip(user_id: str = Query(..., description="User ID to get active trip for"), db: Session = Depends(get_db)):
    """Get the active trip for a user"""
    db_trip = crud.get_active_trip(db, user_id=user_id)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="No active trip found")
    return crud.map_trip_to_response(db_trip)


@app.put("/api/trips/{trip_id}")
def update_trip(trip_id: str, trip: schemas.TripUpdate, db: Session = Depends(get_db)):
    db_trip = crud.update_trip(db, trip_id=trip_id, trip=trip)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return crud.map_trip_to_response(db_trip)

@app.put("/api/trips/{trip_id}/end")
def end_trip(trip_id: str, db: Session = Depends(get_db)):
    """End a trip by marking it as completed"""
    db_trip = crud.end_trip(db, trip_id=trip_id)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    return {
        "message": "Trip ended successfully",
        "tripId": trip_id,
        "ended_at": db_trip.end_date.isoformat() + "Z" if db_trip.end_date else None,
        "status": "completed",
        "delay": db_trip.delay
    }

@app.put("/api/trips/{trip_id}/stats")
def update_trip_stats(trip_id: str, stats: schemas.TripStatsUpdate, db: Session = Depends(get_db)):
    """Update trip statistics (total_distance and duration)"""
    db_trip = crud.update_trip_stats(db, trip_id=trip_id, stats=stats)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    return {
        "message": "Trip stats updated",
        "tripId": trip_id,
        "total_distance": db_trip.total_distance,
        "duration": db_trip.duration
    }

@app.post("/api/trips/{trip_id}/locations")
def add_location(trip_id: str, location: schemas.LocationCreate, db: Session = Depends(get_db)):
    """Add a location to a trip"""
    # First verify the trip exists
    trip = crud.get_trip(db, trip_id=trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Create the location
    db_location = crud.create_location(db, trip_id=trip_id, location=location)
    
    return {
        "location_id": db_location.location_id,
        "trip_id": db_location.trip_id,
        "latitude": db_location.latitude,
        "longitude": db_location.longitude,
        "altitude": db_location.altitude,
        "accuracy": db_location.accuracy,
        "speed": db_location.speed,
        "heading": db_location.heading,
        "timestamp": db_location.timestamp.isoformat() + "Z"
    }

@app.get("/api/trips/{trip_id}/locations")
def get_trip_locations(trip_id: str, skip: int = Query(0, ge=0, description="Number of locations to skip"), 
                       limit: int = Query(100, ge=1, le=1000, description="Maximum number of locations to return"), 
                       db: Session = Depends(get_db)):
    """Get all locations for a trip with pagination"""
    # First verify the trip exists
    trip = crud.get_trip(db, trip_id=trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Get locations for the trip
    locations = crud.get_locations_by_trip(db, trip_id=trip_id, skip=skip, limit=limit)
    
    return [
        {
            "location_id": location.location_id,
            "trip_id": location.trip_id,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "altitude": location.altitude,
            "accuracy": location.accuracy,
            "speed": location.speed,
            "heading": location.heading,
            "timestamp": location.timestamp.isoformat() + "Z"
        }
        for location in locations
    ]

@app.get("/api/trips/{trip_id}/locations/last")
def get_last_location(trip_id: str, db: Session = Depends(get_db)):
    """Get the last (most recent) location for a trip"""
    # First verify the trip exists
    trip = crud.get_trip(db, trip_id=trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Get the last location for the trip
    location = crud.get_last_location_by_trip(db, trip_id=trip_id)
    if location is None:
        raise HTTPException(status_code=404, detail="No locations found for this trip")
    
    return {
        "id": location.location_id,
        "trip_id": location.trip_id,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "altitude": location.altitude,
        "accuracy": location.accuracy,
        "speed": location.speed,
        "heading": location.heading,
        "timestamp": location.timestamp.isoformat() + "Z"
    }

@app.post("/api/trips/{trip_id}/entries")
def add_trip_entry(trip_id: str, entry: schemas.TripEntryCreate, db: Session = Depends(get_db)):
    """Add a trip entry to a trip"""
    # First verify the trip exists
    trip = crud.get_trip(db, trip_id=trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Create the trip entry
    db_entry = crud.create_trip_entry(db, trip_id=trip_id, entry=entry)
    
    return {
        "id": db_entry.step_id,
        "trip_id": db_entry.trip_id,
        "title": db_entry.title,
        "description": db_entry.description,
        "entry_type": db_entry.entry_type,
        "location_name": db_entry.location_name,
        "latitude": db_entry.latitude,
        "longitude": db_entry.longitude,
        "image_urls": db_entry.image_urls,
        "note": db_entry.note,
        "created_at": db_entry.created_at.isoformat() + "Z"
    }

@app.get("/api/trips/{trip_id}/entries")
def get_trip_entries(trip_id: str, skip: int = Query(0, ge=0, description="Number of entries to skip"), 
                     limit: int = Query(100, ge=1, le=1000, description="Maximum number of entries to return"), 
                     db: Session = Depends(get_db)):
    """Get all trip entries for a trip with pagination"""
    # First verify the trip exists
    trip = crud.get_trip(db, trip_id=trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Get entries for the trip
    entries = crud.get_trip_entries_by_trip(db, trip_id=trip_id, skip=skip, limit=limit)
    
    return [
        {
            "id": entry.step_id,
            "trip_id": entry.trip_id,
            "title": entry.title,
            "description": entry.description,
            "entry_type": entry.entry_type,
            "location_name": entry.location_name,
            "latitude": entry.latitude,
            "longitude": entry.longitude,
            "image_urls": entry.image_urls,
            "note": entry.note,
            "created_at": entry.created_at.isoformat() + "Z"
        }
        for entry in entries
    ]

@app.get("/api/users/{user_id}/trips")
def read_user_trips(user_id: str, db: Session = Depends(get_db)):
    trips = crud.get_trips_by_user(db, user_id=user_id)
    return [crud.map_trip_to_response(trip) for trip in trips]

@app.delete("/api/trips/{trip_id}")
def delete_trip(trip_id: str, db: Session = Depends(get_db)):
    deleted_trip = crud.delete_trip(db, trip_id=trip_id)
    if deleted_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return crud.map_trip_to_response(deleted_trip)