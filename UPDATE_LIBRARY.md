# How to Add Games to Library Page

The library page shows games that are in `order_items` linked to `orders` for user_id = 1.

## Quick Methods

### Method 1: Use `add_to_library.py` (Easiest)
```bash
python3 add_to_library.py
```

Or in Python:
```python
from add_to_library import add_game_to_library

# Add a single game (will appear in library immediately)
add_game_to_library(1, "Game Title", "2024-06-20")
```

### Method 2: Use `init_db.py` or `dp.py`
Run these files to initialize/reset the database with sample data:
```bash
python3 init_db.py    # Creates tables and adds initial data
python3 dp.py         # Adds more sample data
```

### Method 3: Direct SQL
```bash
sqlite3 app.db
```

Then:
```sql
-- Add a new game
INSERT INTO games (id, title, genre, price) 
VALUES (9, 'New Game', 'Action', 29.99);

-- Create an order for user 1
INSERT INTO orders (id, user_id, date, order_date, order_status, total_price)
VALUES (6, 1, '2024-06-20', '2024-06-20', 'Completed', 29.99);

-- Add game to order (this makes it appear in library)
INSERT INTO order_items (order_id, game_id, quantity, price_at_purchase)
VALUES (6, 9, 1, 29.99);
```

## Understanding the Library Query

The library page uses this query:
```sql
SELECT games.title, games.genre, orders.date
FROM order_items
JOIN orders ON order_items.order_id = orders.id
JOIN games ON order_items.game_id = games.id
WHERE orders.user_id = 1
ORDER BY {sort} ASC
```

**Important:** 
- Games must be in `order_items` table
- The order must belong to `user_id = 1` (or change USER_ID in app.py)
- Games should have `genre` for sorting by genre
- Orders should have `date` for sorting by date

## Current Library Contents

After running `init_db.py`, the library will show:
- FIFA 25 (Sports) - Jan 15, 2024
- God of War (Action) - Feb 20, 2024
- Minecraft (Sandbox) - Jan 15, 2024
- Elden Ring (RPG) - Mar 10, 2024
- Among Us (Party) - Mar 10, 2024
- Cyberpunk 2077 (RPG) - Apr 5, 2024
- Fortnite (Battle Royale) - May 12, 2024
- Pubg (Battle Royale) - May 12, 2024

## Testing

To see your library:
1. Run `python3 app.py`
2. Visit http://localhost:5001/library
3. You can sort by title, genre, or date

## Files Overview

- **`init_db.py`**: Creates database schema and adds initial data
- **`dp.py`**: Adds additional sample data
- **`add_to_library.py`**: Helper script to easily add games to library
- **`migrate_db.py`**: Updates existing database schema (run once)

