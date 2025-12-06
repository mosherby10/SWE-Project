# How to View Database Results

## Method 1: Use the View Script (Easiest)
```bash
python3 view_db.py
```
This will display all tables in a formatted, readable way.

## Method 2: SQLite3 Command Line
```bash
sqlite3 app.db
```

Then use SQL commands:
```sql
-- View all users
SELECT * FROM users;

-- View all games
SELECT * FROM games;

-- View orders with details
SELECT o.id, u.username, o.date, o.order_status 
FROM orders o 
JOIN users u ON o.user_id = u.id;

-- View activity logs
SELECT * FROM activity_logs ORDER BY date DESC LIMIT 10;

-- Exit sqlite3
.quit
```

## Method 3: Run Flask App (See in Browser)
```bash
python3 app.py
```
Then visit:
- Profile: http://localhost:5001/profile
- Library: http://localhost:5001/library
- Notifications: http://localhost:5001/notifications

## Method 4: Python Interactive Query
```python
import sqlite3

conn = sqlite3.connect("app.db")
cur = conn.cursor()

# Example: Get all users
cur.execute("SELECT * FROM users")
for row in cur.fetchall():
    print(row)

conn.close()
```

## Quick Queries

### Count records:
```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM games;
SELECT COUNT(*) FROM activity_logs;
```

### View specific user:
```sql
SELECT * FROM users WHERE id = 1;
```

### View games with prices:
```sql
SELECT id, title, genre, price FROM games;
```

### View recent activity:
```sql
SELECT action, target_type, date 
FROM activity_logs 
ORDER BY date DESC 
LIMIT 10;
```

