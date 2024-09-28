import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Get the database URL from the environment variable
database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Mask the sensitive parts of the URL
    masked_url = database_url.split("@")[0].split("://")[0] + "://*****:*****@" + database_url.split("@")[1]
    print(f"Database URL found: {masked_url}")

    try:
        # Try to create an engine and connect to the database
        engine = create_engine(database_url)
        with engine.connect() as connection:
            print("Successfully connected to the MariaDB database!")
    except SQLAlchemyError as e:
        print(f"Error connecting to the database: {str(e)}")
else:
    print("DATABASE_URL environment variable not found.")

print("Environment variables:")
for key, value in os.environ.items():
    if key.startswith(("PG", "DATABASE")):
        print(f"{key}: {'*' * len(value)}")  # Mask the actual values
