#!/usr/bin/env python
"""
Database Wipe Script for Django User Management System

This script safely removes all data from the database while preserving the schema.
Use this for testing, development, or when you need a fresh start.

CAUTION: This will delete ALL data in the database!
"""

import os
import sys
import django

import sys
import os
from pathlib import Path

# Add the backend directory to Python path (absolute path, robust)
project_root = Path(__file__).resolve().parent.parent
backend_dir = project_root / 'backend'
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.authtoken.models import Token

User = get_user_model()

def confirm_action():
    """Ask for user confirmation before proceeding"""
    print("⚠️  WARNING: This will DELETE ALL DATA from the database!")
    print("   - All users will be removed")
    print("   - All authentication tokens will be removed")
    print("   - This action CANNOT be undone!")
    print()
    
    response = input("Are you sure you want to continue? Type 'YES' to confirm: ")
    return response.strip() == 'YES'

def wipe_all_data():
    """Wipe all data from the database"""
    try:
        with transaction.atomic():
            print("🧹 Starting database cleanup...")
            
            # Count existing data
            user_count = User.objects.count()
            token_count = Token.objects.count()
            
            print(f"📊 Current data:")
            print(f"   - Users: {user_count}")
            print(f"   - Tokens: {token_count}")
            print()
            
            if user_count == 0 and token_count == 0:
                print("✅ Database is already empty!")
                return True
            
            # Delete all tokens first (to avoid foreign key issues)
            print("🔑 Deleting authentication tokens...")
            deleted_tokens = Token.objects.all().delete()
            print(f"   ✅ Deleted {deleted_tokens[0]} tokens")
            
            # Delete all users
            print("👥 Deleting all users...")
            deleted_users = User.objects.all().delete()
            print(f"   ✅ Deleted {deleted_users[0]} users")
            
            print()
            print("🎉 Database wipe completed successfully!")
            print("📋 Summary:")
            print(f"   - Users deleted: {user_count}")
            print(f"   - Tokens deleted: {token_count}")
            print("   - Database schema preserved")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during database wipe: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_fresh_superuser():
    """Optionally create a new superuser after wiping"""
    print("\n🔧 Would you like to create a new superuser?")
    response = input("Create superuser? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        try:
            print("\n👤 Creating new superuser...")
            
            username = input("Username (admin): ").strip() or "admin"
            email = input("Email (admin@example.com): ").strip() or "admin@example.com"
            
            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password='admin123',  # Default password
                role='admin'
            )
            
            print(f"✅ Superuser created successfully!")
            print(f"   - Username: {username}")
            print(f"   - Email: {email}")
            print(f"   - Password: admin123")
            print(f"   - Role: admin")
            print("\n⚠️  Remember to change the password after first login!")
            
        except Exception as e:
            print(f"❌ Error creating superuser: {e}")

def main():
    """Main function"""
    print("🗑️  Django User Management System - Database Wipe Tool")
    print("=" * 60)
    print()
    
    # Check if we're in the right directory
    if not (Path.cwd() / 'backend' / 'manage.py').exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   (The directory containing the 'backend' folder)")
        sys.exit(1)
    
    # Confirm action
    if not confirm_action():
        print("❌ Operation cancelled by user")
        sys.exit(0)
    
    print("\n🚀 Starting database wipe...")
    
    # Perform the wipe
    if wipe_all_data():
        # Optionally create a new superuser
        create_fresh_superuser()
        
        print("\n✨ Database wipe completed!")
        print("\n📝 Next steps:")
        print("   1. Start the Django server: cd backend && python manage.py runserver")
        print("   2. Start the frontend: python frontend/main.py")
        print("   3. Register new users or use the superuser account")
        
    else:
        print("❌ Database wipe failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
