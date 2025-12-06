import sqlite3
from datetime import datetime

conn = sqlite3.connect("app.db")
cur = conn.cursor()

print("=" * 80)
print("DATABASE CONTENTS - app.db")
print("=" * 80)

# Users
print("\n📊 USERS TABLE")
print("-" * 80)
cur.execute("SELECT id, username, name, email, country, bio, account_status, date_created FROM users")
users = cur.fetchall()
print(f"Total users: {len(users)}\n")
for user in users:
    print(f"ID: {user[0]}")
    print(f"  Username: {user[1]}")
    print(f"  Name: {user[2]}")
    print(f"  Email: {user[3]}")
    print(f"  Country: {user[4] or 'N/A'}")
    print(f"  Bio: {user[5] or 'N/A'}")
    print(f"  Status: {user[6] or 'Active'}")
    print(f"  Created: {user[7] or 'N/A'}")
    print()

# Games
print("\n🎮 GAMES TABLE")
print("-" * 80)
cur.execute("SELECT id, title, genre, price FROM games")
games = cur.fetchall()
print(f"Total games: {len(games)}\n")
for game in games:
    print(f"ID: {game[0]}")
    print(f"  Title: {game[1]}")
    print(f"  Genre: {game[2] or 'N/A'}")
    print(f"  Price: ${game[3]:.2f}" if game[3] else "  Price: Free")
    print()

# Orders
print("\n🛒 ORDERS TABLE")
print("-" * 80)
cur.execute("SELECT id, user_id, date, order_date, total_price, order_status FROM orders")
orders = cur.fetchall()
print(f"Total orders: {len(orders)}\n")
for order in orders:
    print(f"ID: {order[0]}")
    print(f"  User ID: {order[1]}")
    print(f"  Date: {order[2] or order[3] or 'N/A'}")
    print(f"  Total Price: ${order[4]:.2f}" if order[4] else "  Total Price: N/A")
    print(f"  Status: {order[5] or 'N/A'}")
    print()

# Order Items
print("\n📦 ORDER ITEMS TABLE")
print("-" * 80)
cur.execute("SELECT id, order_id, game_id, quantity, price_at_purchase FROM order_items")
order_items = cur.fetchall()
print(f"Total order items: {len(order_items)}\n")
for item in order_items:
    print(f"ID: {item[0]}")
    print(f"  Order ID: {item[1]}")
    print(f"  Game ID: {item[2]}")
    print(f"  Quantity: {item[3] or 1}")
    print(f"  Price at Purchase: ${item[4]:.2f}" if item[4] else "  Price at Purchase: N/A")
    print()

# Notifications
print("\n🔔 NOTIFICATIONS TABLE")
print("-" * 80)
cur.execute("SELECT id, user_id, message, is_read, created_at FROM notifications ORDER BY id DESC LIMIT 10")
notifications = cur.fetchall()
print(f"Showing last 10 notifications (Total: {len(notifications)})\n")
for notif in notifications:
    print(f"ID: {notif[0]}")
    print(f"  User ID: {notif[1]}")
    print(f"  Message: {notif[2]}")
    print(f"  Read: {'Yes' if notif[3] else 'No'}")
    print(f"  Created: {notif[4]}")
    print()

# Admins
print("\n👤 ADMINS TABLE")
print("-" * 80)
cur.execute("SELECT id, name, email FROM admins")
admins = cur.fetchall()
print(f"Total admins: {len(admins)}\n")
if admins:
    for admin in admins:
        print(f"ID: {admin[0]}")
        print(f"  Name: {admin[1]}")
        print(f"  Email: {admin[2]}")
        print()
else:
    print("No admins in database")

# Activity Logs
print("\n📝 ACTIVITY LOGS TABLE")
print("-" * 80)
cur.execute("SELECT id, admin_id, action, target_type, target_id, details, date FROM activity_logs ORDER BY date DESC LIMIT 10")
logs = cur.fetchall()
print(f"Showing last 10 activity logs (Total: {len(logs)})\n")
for log in logs:
    print(f"ID: {log[0]}")
    print(f"  Admin ID: {log[1]}")
    print(f"  Action: {log[2]}")
    print(f"  Target: {log[3]} (ID: {log[4] or 'N/A'})")
    print(f"  Details: {log[5] or 'N/A'}")
    print(f"  Date: {log[6]}")
    print()

print("=" * 80)
print("END OF DATABASE CONTENTS")
print("=" * 80)

conn.close()

