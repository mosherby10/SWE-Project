import sqlite3

# Connect to the database (it will create app.db if it doesn't exist)
conn = sqlite3.connect("app.db")
cur = conn.cursor()

# ============================
# CREATE TABLES
# ============================

# Users table - merged schema from existing and store.dp
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    country TEXT,
    bio TEXT,
    avatar TEXT,
    account_status TEXT DEFAULT 'Active',
    date_created DATETIME
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    is_read INTEGER DEFAULT 0,
    created_at TEXT
);
""")

# Games table - merged schema (added price from store.dp, kept genre)
cur.execute("""
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY,
    title TEXT,
    genre TEXT,
    price NUMERIC(10, 2)
);
""")

# Orders table - merged schema (added order_date, total_price, order_status from store.dp)
cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    order_date DATETIME,
    total_price NUMERIC(10, 2),
    order_status TEXT
);
""")

# Order items table - merged schema (added quantity, price_at_purchase from store.dp)
cur.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    game_id INTEGER,
    quantity INTEGER,
    price_at_purchase NUMERIC(10, 2)
);
""")

# New tables from store.dp
cur.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
);
""")

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

# ============================
# INSERT SAMPLE DATA
# ============================

# Users - existing data plus data from store.dp
cur.execute("""
INSERT OR IGNORE INTO users (id, username, name, email, country, bio, avatar, password, account_status, date_created)
VALUES (1, 'ibraheem123', 'Ibraheem', 'ibraheem@example.com', 'Egypt', 'Gamer & Dev', 'default.png', NULL, 'Active', datetime('now'));
""")

# Additional users from store.dp
cur.execute("""
INSERT OR IGNORE INTO users (id, username, name, email, password, account_status, date_created)
VALUES 
    (2, 'ahmed', 'Ahmed', 'ahmed@example.com', 'hashed_pw1', 'Active', '2025-12-04 12:00:00'),
    (3, 'sara', 'Sara', 'sara@example.com', 'hashed_pw2', 'Active', '2025-12-04 12:05:00'),
    (4, 'omar', 'Omar', 'omar@example.com', 'hashed_pw3', 'Active', '2025-12-04 12:10:00'),
    (5, 'lina', 'Lina', 'lina@example.com', 'hashed_pw4', 'Active', '2025-12-04 12:15:00'),
    (6, 'youssef', 'Youssef', 'youssef@example.com', 'hashed_pw5', 'Banned', '2025-12-04 12:20:00');
""")

# Games - existing data plus data from store.dp (with genres for library sorting)
cur.execute("INSERT OR IGNORE INTO games (id, title, genre, price) VALUES (1, 'FIFA 25', 'Sports', 59.99)")
cur.execute("INSERT OR IGNORE INTO games (id, title, genre, price) VALUES (2, 'God of War', 'Action', 49.99)")
cur.execute("INSERT OR IGNORE INTO games (id, title, genre, price) VALUES (3, 'Minecraft', 'Sandbox', 26.95)")

# Additional games from store.dp (adding genres so they appear in library)
cur.execute("""
INSERT OR IGNORE INTO games (id, title, genre, price) VALUES
    (4, 'Elden Ring', 'RPG', 59.99),
    (5, 'Among Us', 'Party', 4.99),
    (6, 'Cyberpunk 2077', 'RPG', 49.99),
    (7, 'Fortnite', 'Battle Royale', 0.00),
    (8, 'Pubg', 'Battle Royale', 0.00);
""")

# Orders - multiple orders for user_id=1 so games appear in library page
# Order 1: January 2024
cur.execute("INSERT OR IGNORE INTO orders (id, user_id, date, order_date, order_status, total_price) VALUES (1, 1, '2024-01-15', '2024-01-15', 'Completed', 86.94)")
cur.execute("INSERT OR IGNORE INTO order_items (order_id, game_id, quantity, price_at_purchase) VALUES (1, 1, 1, 59.99)")  # FIFA 25
cur.execute("INSERT OR IGNORE INTO order_items (order_id, game_id, quantity, price_at_purchase) VALUES (1, 3, 1, 26.95)")  # Minecraft

# Order 2: February 2024
cur.execute("INSERT OR IGNORE INTO orders (id, user_id, date, order_date, order_status, total_price) VALUES (2, 1, '2024-02-20', '2024-02-20', 'Completed', 49.99)")
cur.execute("INSERT OR IGNORE INTO order_items (order_id, game_id, quantity, price_at_purchase) VALUES (2, 2, 1, 49.99)")  # God of War

# Order 3: March 2024
cur.execute("INSERT OR IGNORE INTO orders (id, user_id, date, order_date, order_status, total_price) VALUES (3, 1, '2024-03-10', '2024-03-10', 'Completed', 64.98)")
cur.execute("INSERT OR IGNORE INTO order_items (order_id, game_id, quantity, price_at_purchase) VALUES (3, 4, 1, 59.99)")  # Elden Ring
cur.execute("INSERT OR IGNORE INTO order_items (order_id, game_id, quantity, price_at_purchase) VALUES (3, 5, 1, 4.99)")  # Among Us

# Order 4: April 2024
cur.execute("INSERT OR IGNORE INTO orders (id, user_id, date, order_date, order_status, total_price) VALUES (4, 1, '2024-04-05', '2024-04-05', 'Completed', 49.99)")
cur.execute("INSERT OR IGNORE INTO order_items (order_id, game_id, quantity, price_at_purchase) VALUES (4, 6, 1, 49.99)")  # Cyberpunk 2077

# Order 5: May 2024 (Free games)
cur.execute("INSERT OR IGNORE INTO orders (id, user_id, date, order_date, order_status, total_price) VALUES (5, 1, '2024-05-12', '2024-05-12', 'Completed', 0.00)")
cur.execute("INSERT OR IGNORE INTO order_items (order_id, game_id, quantity, price_at_purchase) VALUES (5, 7, 1, 0.00)")  # Fortnite
cur.execute("INSERT OR IGNORE INTO order_items (order_id, game_id, quantity, price_at_purchase) VALUES (5, 8, 1, 0.00)")  # Pubg

cur.execute("""
INSERT OR IGNORE INTO notifications (user_id, message, created_at)
VALUES (1, 'Welcome to your Notification Center!', datetime('now'))
""")

conn.commit()
conn.close()

print("Database initialized successfully!")
