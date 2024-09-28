import os
import csv
import zipfile
import sqlite3
from datetime import datetime

def import_data_from_backup():
    # Get the latest backup file
    backup_files = [f for f in os.listdir('.') if f.startswith('database_backup_') and f.endswith('.zip')]
    if not backup_files:
        print("No backup files found.")
        return

    latest_backup = max(backup_files)
    print(f"Using backup file: {latest_backup}")

    # Connect to the SQLite database
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    with zipfile.ZipFile(latest_backup, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            table_name = os.path.splitext(file_name)[0]
            print(f"Importing data for table: {table_name}")

            with zip_ref.open(file_name) as csvfile:
                csv_reader = csv.reader(csvfile.read().decode('utf-8').splitlines())
                headers = next(csv_reader)
                
                # Create table if it doesn't exist
                columns = ', '.join([f"{header} TEXT" for header in headers])
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")

                # Insert data
                for row in csv_reader:
                    placeholders = ', '.join(['?' for _ in row])
                    cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)

    conn.commit()
    conn.close()
    print("Data import completed successfully.")

if __name__ == "__main__":
    import_data_from_backup()
