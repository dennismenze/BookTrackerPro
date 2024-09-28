import os
import csv
import zipfile
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from models import db, User, Book, Author, List, UserBook

# Get database connection details from environment variables
database_url = os.environ.get('DATABASE_URL')

# Create a timestamp for the backup files
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_folder = f"database_backup_{timestamp}"
os.makedirs(backup_folder, exist_ok=True)

try:
    # Create SQLAlchemy engine
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Get all table names
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    # Export data from each table
    for table_name in table_names:
        query = text(f"SELECT * FROM {table_name}")
        result = session.execute(query)
        
        file_path = os.path.join(backup_folder, f"{table_name}.csv")
        with open(file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(result.keys())
            csv_writer.writerows(result)

    # Create a zip file containing all CSV files
    zip_file_path = f"{backup_folder}.zip"
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, _, files in os.walk(backup_folder):
            for file in files:
                zipf.write(os.path.join(root, file), file)

    print(f"Database export completed successfully. Backup file: {zip_file_path}")

except Exception as e:
    print(f"An error occurred during the database export: {str(e)}")

finally:
    # Clean up the temporary backup folder
    for root, _, files in os.walk(backup_folder, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
    os.rmdir(backup_folder)
    
    # Close the database session
    session.close()
