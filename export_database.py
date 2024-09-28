import os
import subprocess
from datetime import datetime

# Get database connection details from environment variables
db_name = os.environ.get('PGDATABASE')
db_user = os.environ.get('PGUSER')
db_host = os.environ.get('PGHOST')
db_password = os.environ.get('PGPASSWORD')
db_port = os.environ.get('PGPORT')

# Create a timestamp for the backup file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"database_backup_{timestamp}.sql"

# Construct the pg_dump command
pg_dump_command = [
    "pg_dump",
    f"--dbname=postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
    "--format=plain",
    "--no-owner",
    "--no-acl",
    f"--file={backup_file}"
]

try:
    # Execute the pg_dump command
    subprocess.run(pg_dump_command, check=True)
    print(f"Database export completed successfully. Backup file: {backup_file}")
except subprocess.CalledProcessError as e:
    print(f"Error exporting database: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
