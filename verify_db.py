"""
Quick script to verify the database schema is correct
"""
import sqlite3
import os

db_path = os.path.join('instance', 'gaming_store.db')

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all columns from users table
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("Users table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check specifically for profile_photo
        column_names = [col[1] for col in columns]
        if 'profile_photo' in column_names:
            print("\n✓ profile_photo column exists!")
        else:
            print("\n✗ profile_photo column is MISSING!")
            print("Run the migration script or restart the Flask app to add it.")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
else:
    print(f"Database not found at {db_path}")
    print("The database will be created when you run the Flask app.")
