import sqlite3
import os

# Backup existing database
if os.path.exists("app.db"):
    print("Backing up existing app.db...")
    import shutil
    shutil.copy("app.db", "app.db.backup")

# Connect to database
conn = sqlite3.connect("app.db")
cur = conn.cursor()

# Add new columns to existing tables if they don't exist
print("Migrating database schema...")

# Add columns to users table
try:
    cur.execute("ALTER TABLE users ADD COLUMN password TEXT")
    print("Added password column to users")
except sqlite3.OperationalError:
    pass  # Column already exists

try:
    cur.execute("ALTER TABLE users ADD COLUMN account_status TEXT DEFAULT 'Active'")
    print("Added account_status column to users")
except sqlite3.OperationalError:
    pass

try:
    cur.execute("ALTER TABLE users ADD COLUMN date_created DATETIME")
    print("Added date_created column to users")
except sqlite3.OperationalError:
    pass

# Add UNIQUE constraint to email if not exists (SQLite doesn't support ADD CONSTRAINT, so we'll handle it in init)
try:
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    print("Added unique index on users.email")
except sqlite3.OperationalError:
    pass

# Add columns to games table
try:
    cur.execute("ALTER TABLE games ADD COLUMN price NUMERIC(10, 2)")
    print("Added price column to games")
except sqlite3.OperationalError:
    pass

# Add columns to orders table
try:
    cur.execute("ALTER TABLE orders ADD COLUMN order_date DATETIME")
    print("Added order_date column to orders")
except sqlite3.OperationalError:
    pass

try:
    cur.execute("ALTER TABLE orders ADD COLUMN total_price NUMERIC(10, 2)")
    print("Added total_price column to orders")
except sqlite3.OperationalError:
    pass

try:
    cur.execute("ALTER TABLE orders ADD COLUMN order_status TEXT")
    print("Added order_status column to orders")
except sqlite3.OperationalError:
    pass

# Add columns to order_items table
try:
    cur.execute("ALTER TABLE order_items ADD COLUMN quantity INTEGER")
    print("Added quantity column to order_items")
except sqlite3.OperationalError:
    pass

try:
    cur.execute("ALTER TABLE order_items ADD COLUMN price_at_purchase NUMERIC(10, 2)")
    print("Added price_at_purchase column to order_items")
except sqlite3.OperationalError:
    pass

# Create new tables
cur.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
);
""")
print("Created admins table")

cur.execute("""
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER,
    action TEXT,
    target_type TEXT,
    target_id INTEGER,
    details TEXT,
    date DATETIME
);
""")
print("Created activity_logs table")

conn.commit()
conn.close()

print("Database migration completed!")

