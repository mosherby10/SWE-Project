import sqlite3

conn = sqlite3.connect("app.db")
cur = conn.cursor()

# Insert user
cur.execute("""
INSERT OR IGNORE INTO users (id, username, name, email, country, bio, avatar, password, account_status, date_created)
VALUES (1, 'ibraheem123', 'Ibraheem', 'ibraheem@example.com', 'Egypt', 'Gamer & Developer', 'default.png', NULL, 'Active', datetime('now'));
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

# Notifications
cur.execute("""
INSERT OR IGNORE INTO notifications (user_id, message, is_read, created_at) VALUES
(1, 'Welcome to the platform!', 0, datetime('now')),
(1, 'Your profile was viewed recently.', 0, datetime('now')),
(1, 'New update available!', 1, datetime('now'));
""")

# Games - existing plus from store.dp (with genres for library sorting)
cur.execute("""
INSERT OR IGNORE INTO games (id, title, genre, price) VALUES
(1, 'FIFA 25', 'Sports', 59.99),
(2, 'Call of Duty', 'Action', 49.99),
(3, 'Minecraft', 'Sandbox', 26.95);
""")

# Additional games from store.dp (adding genres so they appear in library)
cur.execute("""
INSERT OR IGNORE INTO games (id, title, genre, price) VALUES
    (4, 'Elden Ring', 'RPG', 59.99),
    (5, 'Among Us', 'Party', 4.99),
    (6, 'Cyberpunk 2077', 'RPG', 49.99),
    (7, 'Fortnite', 'Battle Royale', 0.00),
    (8, 'Pubg', 'Battle Royale', 0.00);
""")

# Orders & order items - multiple orders for user_id=1 so games appear in library page
# Order 1: January 2024
cur.execute("INSERT OR IGNORE INTO orders (id, user_id, date, order_date, order_status, total_price) VALUES (1, 1, '2024-01-15', '2024-01-15', 'Completed', 86.94)")
cur.execute("INSERT OR IGNORE INTO order_items (order_id, game_id, quantity, price_at_purchase) VALUES (1, 1, 1, 59.99)")  # FIFA 25
cur.execute("INSERT OR IGNORE INTO order_items (order_id, game_id, quantity, price_at_purchase) VALUES (1, 3, 1, 26.95)")  # Minecraft

# Order 2: February 2024
cur.execute("INSERT OR IGNORE INTO orders (id, user_id, date, order_date, order_status, total_price) VALUES (2, 1, '2024-02-20', '2024-02-20', 'Completed', 49.99)")
cur.execute("INSERT OR IGNORE INTO order_items (order_id, game_id, quantity, price_at_purchase) VALUES (2, 2, 1, 49.99)")  # Call of Duty / God of War

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

# Sample activity logs from store.dp
cur.execute("""
INSERT OR IGNORE INTO activity_logs (admin_id, action, target_type, target_id, details, date) VALUES
(1, 'seed_data', 'system', NULL, NULL, '2025-12-04 16:10:29.430956'),
(1, 'ban_user', 'user', 6, NULL, '2025-12-04 16:20:05.809677'),
(1, 'delete_user', 'user', 2, NULL, '2025-12-04 16:20:48.494623'),
(1, 'edit_user', 'user', 1, NULL, '2025-12-04 17:12:08.353507'),
(1, 'add_game', 'game', 1, NULL, '2025-12-04 18:17:39.067159'),
(1, 'edit_game', 'game', 1, NULL, '2025-12-04 18:21:14.492193'),
(1, 'edit_game', 'game', 1, NULL, '2025-12-04 18:23:24.362229'),
(1, 'add_game', 'game', 2, NULL, '2025-12-04 18:23:55.767383'),
(1, 'unban_user', 'user', 6, NULL, '2025-12-04 18:24:11.840614'),
(1, 'edit_user', 'user', 1, NULL, '2025-12-04 18:24:14.813852'),
(1, 'add_game', 'game', 3, NULL, '2025-12-04 18:39:12.486024'),
(1, 'delete_game', 'game', 1, NULL, '2025-12-04 18:46:14.848702'),
(1, 'cancel_order', 'order', 2, 'Admin cancelled order #2', '2025-12-04 18:52:53.560621'),
(1, 'delete_game', 'game', 3, NULL, '2025-12-04 19:03:50.760753'),
(1, 'add_game', 'game', 3, NULL, '2025-12-04 19:03:59.504247'),
(1, 'add_game', 'game', 4, NULL, '2025-12-04 19:28:28.675060'),
(1, 'edit_user', 'user', 1, NULL, '2025-12-04 19:28:58.172927'),
(1, 'ban_user', 'user', 6, NULL, '2025-12-04 19:44:07.188036'),
(1, 'edit_user', 'user', 1, NULL, '2025-12-04 19:44:10.051622'),
(1, 'edit_user', 'user', 1, NULL, '2025-12-04 19:44:18.785048'),
(1, 'unban_user', 'user', 6, NULL, '2025-12-04 19:44:20.345257'),
(1, 'edit_user', 'user', 1, NULL, '2025-12-04 19:44:21.952162'),
(1, 'edit_game', 'game', 2, NULL, '2025-12-04 19:45:55.574798'),
(1, 'delete_game', 'game', 3, NULL, '2025-12-04 19:46:05.073189'),
(1, 'edit_game', 'game', 4, NULL, '2025-12-04 20:06:25.349344'),
(1, 'delete_game', 'game', 4, NULL, '2025-12-04 20:06:41.084808'),
(1, 'ban_user', 'user', 3, NULL, '2025-12-04 20:41:12.198349'),
(1, 'edit_game', 'game', 3, NULL, '2025-12-04 20:41:32.592994'),
(1, 'unban_user', 'user', 3, NULL, '2025-12-04 20:44:32.032359'),
(1, 'edit_game', 'game', 2, NULL, '2025-12-04 20:46:48.734611'),
(1, 'add_game', 'game', 6, NULL, '2025-12-04 20:47:05.635384'),
(1, 'cancel_order', 'order', 4, 'Admin cancelled order #4', '2025-12-05 03:14:58.921018'),
(1, 'delete_game', 'game', 6, NULL, '2025-12-05 14:07:20.711625');
""")

conn.commit()
conn.close()

print("Sample data added!")
