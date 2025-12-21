# How to Run the Application

## Running the Application

**You should run `app.py`** - This is the main entry point that uses the Factory Pattern.

```bash
cd SWE-Project
python app.py
```

The `app.py` file uses the `app_factory.py` to create the Flask application instance following the Factory Pattern.

## Application Structure

- **`app.py`** - Main entry point (run this file)
- **`app_factory.py`** - Application factory that creates and configures the Flask app
- **`controllers/`** - All route handlers (MVC Controllers)
- **`models/`** - Database models (MVC Models)
- **`views/`** - HTML templates (MVC Views)
- **`repositories/`** - Database access layer (Repository Pattern)
- **`static/`** - CSS, JavaScript, and image files

## Features

- ✅ MVC Architecture
- ✅ Factory Pattern (App Factory)
- ✅ Repository Pattern
- ✅ Singleton Pattern (Database)
- ✅ Dark/Light Theme Toggle
- ✅ Arabic/English Language Support
- ✅ Wishlist Functionality
- ✅ About Us Page
- ✅ Enhanced Notifications

## Default Credentials

- **Admin**: admin@admin.com / admin123
- **Users**: Register a new account

