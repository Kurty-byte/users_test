#!/usr/bin/env python
"""
Database Preview Script for Django User Management System

This script shows what data exists in the database without deleting anything.
Use this to preview data before running wipe_all.py
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
from rest_framework.authtoken.models import Token

User = get_user_model()

def preview_database():
    """Preview all data in the database"""
    print("📊 Database Content Preview")
    print("=" * 50)
    
    # Count data
    user_count = User.objects.count()
    token_count = Token.objects.count()
    
    print(f"📈 Summary:")
    print(f"   - Total Users: {user_count}")
    print(f"   - Total Tokens: {token_count}")
    print()
    
    if user_count == 0:
        print("📭 No users found in database")
    else:
        print("👥 Users in database:")
        print("-" * 30)
        for user in User.objects.all():
            active_status = "✅ Active" if user.is_active else "❌ Inactive"
            superuser_status = "👑 Superuser" if user.is_superuser else ""
            print(f"   ID: {user.id:<3} | {user.username:<15} | {user.email:<25} | {user.role:<8} | {active_status} {superuser_status}")
    
    print()
    
    if token_count == 0:
        print("🔑 No authentication tokens found")
    else:
        print("🔑 Authentication tokens:")
        print("-" * 30)
        for token in Token.objects.all():
            print(f"   User: {token.user.username:<15} | Token: {str(token.key)[:20]}...")
    
    print()
    print("💡 Tips:")
    print("   - Run 'python wipe_all.py' to delete all data")
    print("   - Run 'cd backend && python manage.py createsuperuser' to create admin")
    print("   - Run 'cd backend && python manage.py runserver' to start server")

def main():
    """Main function"""
    print("🔍 Django User Management System - Database Preview")
    print("=" * 60)
    print()
    
    # Check if we're in the right directory
    if not (Path.cwd() / 'backend' / 'manage.py').exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   (The directory containing the 'backend' folder)")
        sys.exit(1)
    
    try:
        preview_database()
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        print("\n💡 Make sure:")
        print("   - The Django backend is properly configured")
        print("   - The database file exists (backend/db.sqlite3)")
        print("   - All dependencies are installed")
        sys.exit(1)

if __name__ == '__main__':
    main()
