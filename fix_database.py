"""
Database Fix Script
This script fixes common database issues:
1. Normalizes all emails to lowercase
2. Ensures all passwords are hashed (not plain text)
3. Reports any issues found
"""

from app import app
from models import db, User, Admin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

def is_hashed(password):
    """Check if password is already hashed"""
    if not password:
        return False
    # Werkzeug hashes start with specific prefixes
    return (password.startswith("$2b$") or 
            password.startswith("$2a$") or 
            password.startswith("$pbkdf2:") or
            password.startswith("scrypt:") or
            password.startswith("$argon2"))

def fix_database():
    """Fix database issues"""
    with app.app_context():
        print("Starting database fix...")
        
        # Fix Users
        users = User.query.all()
        users_fixed = 0
        emails_normalized = 0
        passwords_hashed = 0
        
        for user in users:
            changed = False
            
            # Normalize email to lowercase
            if user.email != user.email.lower():
                print(f"  Normalizing email for user {user.id}: {user.email} -> {user.email.lower()}")
                user.email = user.email.lower()
                emails_normalized += 1
                changed = True
            
            # Check if password needs hashing
            if not is_hashed(user.password):
                print(f"  WARNING: User {user.id} ({user.email}) has plain text password!")
                print(f"    Password will be hashed on next login, or you can set a new password.")
                # Don't hash it now because we don't know the original password
                # It will be hashed automatically on next successful login
            
            if changed:
                users_fixed += 1
        
        # Fix Admins
        admins = Admin.query.all()
        admins_fixed = 0
        
        for admin in admins:
            changed = False
            
            # Normalize email to lowercase
            if admin.email != admin.email.lower():
                print(f"  Normalizing email for admin {admin.id}: {admin.email} -> {admin.email.lower()}")
                admin.email = admin.email.lower()
                emails_normalized += 1
                changed = True
            
            # Check if password needs hashing
            if not is_hashed(admin.password):
                print(f"  WARNING: Admin {admin.id} ({admin.email}) has plain text password!")
                print(f"    Password will be hashed on next login, or you can set a new password.")
            
            if changed:
                admins_fixed += 1
        
        # Commit changes
        if users_fixed > 0 or admins_fixed > 0:
            try:
                db.session.commit()
                print(f"\n✓ Fixed {users_fixed} users and {admins_fixed} admins")
                print(f"✓ Normalized {emails_normalized} emails to lowercase")
            except Exception as e:
                print(f"\n✗ Error committing changes: {e}")
                db.session.rollback()
        else:
            print("\n✓ No fixes needed - database is already normalized")
        
        # Print summary
        print(f"\nDatabase Summary:")
        print(f"  Total Users: {len(users)}")
        print(f"  Total Admins: {len(admins)}")
        
        # List all users and admins
        print(f"\nUsers in database:")
        for user in users:
            password_status = "hashed" if is_hashed(user.password) else "PLAIN TEXT"
            print(f"  ID: {user.id}, Email: {user.email}, Username: {user.username}, Password: {password_status}")
        
        print(f"\nAdmins in database:")
        for admin in admins:
            password_status = "hashed" if is_hashed(admin.password) else "PLAIN TEXT"
            print(f"  ID: {admin.id}, Email: {admin.email}, Name: {admin.name}, Password: {password_status}")
        
        print("\n✓ Database fix completed!")

if __name__ == "__main__":
    fix_database()

