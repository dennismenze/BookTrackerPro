import sqlite3

def check_import():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Table {table_name}: {count} records")

    conn.close()

if __name__ == "__main__":
    check_import()
