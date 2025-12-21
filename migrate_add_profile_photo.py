"""
Migration script to add profile_photo column to users table
Run this script once to update your database schema
"""
import sqlite3
import os
import sys

# Path to the database
db_path = os.path.join('instance', 'gaming_store.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    print("The database will be created when you run app.py")
    sys.exit(1)

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(users)")
    columns_info = cursor.fetchall()
    columns = [column[1] for column in columns_info]
    
    print(f"Current columns in users table: {columns}")
    
    if 'profile_photo' in columns:
        print("✓ Column 'profile_photo' already exists in users table.")
    else:
        # Add the profile_photo column
        print("Adding 'profile_photo' column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN profile_photo VARCHAR(255)")
        conn.commit()
        print("✓ Successfully added 'profile_photo' column to users table!")
    
    # Verify the column was added
    cursor.execute("PRAGMA table_info(users)")
    columns_info = cursor.fetchall()
    columns = [column[1] for column in columns_info]
    print(f"Updated columns in users table: {columns}")
    
    conn.close()
    print("\n✓ Migration completed successfully!")
    
except sqlite3.Error as e:
    print(f"✗ Database error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
