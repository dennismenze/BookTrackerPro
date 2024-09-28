import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Get the database URL from the environment variable or use the default SQLite URL
database_url = os.environ.get("DATABASE_URL", "sqlite:///book_tracker.db")

print(f"Database URL found: {database_url}")

try:
    # Try to create an engine and connect to the database
    engine = create_engine(database_url)
    with engine.connect() as connection:
        print("Successfully connected to the SQLite database!")
except SQLAlchemyError as e:
    print(f"Error connecting to the database: {str(e)}")

print("Environment variables:")
for key, value in os.environ.items():
    if key.startswith(("DATABASE",)):
        print(f"{key}: {'*' * len(value)}")  # Mask the actual values
