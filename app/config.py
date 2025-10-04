import os

# Normally load from env vars (.env file + python-dotenv), here hardcoded for clarity
DB_USER = os.getenv("DB_USER", "travel_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "travel_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "travel_schema")

SQLALCHEMY_DATABASE_URL = (
    f"mysql+mysqldb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Table names
USERS_TABLE = "users"
TRIPS_TABLE = "trips"
LOCATIONS_TABLE = "locations"
TRIP_ENTRIES_TABLE = "trip_entries"
