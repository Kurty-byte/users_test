#!/usr/bin/env python
"""
Database Population Script for Django User Management System

This script populates the database with sample users for testing and development.
Creates 3 faculty, 3 staff, and 5 students with default password: password123
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.append(str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.authtoken.models import Token

User = get_user_model()

# Sample user data
SAMPLE_USERS = {
    'faculty': [
        {
            'username': 'prof_johnson',
            'email': 'johnson@university.edu',
            'first_name': 'Emily',
            'last_name': 'Johnson',
            'role': 'faculty'
        },
        {
            'username': 'prof_williams',
            'email': 'williams@university.edu',
            'first_name': 'Michael',
            'last_name': 'Williams',
            'role': 'faculty'
        },
        {
            'username': 'prof_davis',
            'email': 'davis@university.edu',
            'first_name': 'Sarah',
            'last_name': 'Davis',
            'role': 'faculty'
        }
    ],
    'staff': [
        {
            'username': 'staff_anderson',
            'email': 'anderson@university.edu',
            'first_name': 'James',
            'last_name': 'Anderson',
            'role': 'staff'
        },
        {
            'username': 'staff_taylor',
            'email': 'taylor@university.edu',
            'first_name': 'Lisa',
            'last_name': 'Taylor',
            'role': 'staff'
        },
        {
            'username': 'staff_brown',
            'email': 'brown@university.edu',
            'first_name': 'David',
            'last_name': 'Brown',
            'role': 'staff'
        }
    ],
    'student': [
        {
            'username': 'student_miller',
            'email': 'miller@student.university.edu',
            'first_name': 'Alex',
            'last_name': 'Miller',
            'role': 'student'
        },
        {
            'username': 'student_wilson',
            'email': 'wilson@student.university.edu',
            'first_name': 'Emma',
            'last_name': 'Wilson',
            'role': 'student'
        },
        {
            'username': 'student_moore',
            'email': 'moore@student.university.edu',
            'first_name': 'Ryan',
            'last_name': 'Moore',
            'role': 'student'
        },
        {
            'username': 'student_garcia',
            'email': 'garcia@student.university.edu',
            'first_name': 'Sofia',
            'last_name': 'Garcia',
            'role': 'student'
        },
        {
            'username': 'student_martinez',
            'email': 'martinez@student.university.edu',
            'first_name': 'Carlos',
            'last_name': 'Martinez',
            'role': 'student'
        }
    ]
}

DEFAULT_PASSWORD = 'password123'

def check_existing_users():
    """Check if users already exist"""
    existing_count = User.objects.count()
    
    if existing_count > 0:
        print(f"⚠️  Database already contains {existing_count} users.")
        print("   Existing users:")
        for user in User.objects.all()[:10]:  # Show first 10
            print(f"   - {user.username} ({user.email}) - {user.role}")
        
        if existing_count > 10:
            print(f"   ... and {existing_count - 10} more")
        
        print()
        response = input("Do you want to add sample users anyway? (y/N): ").strip().lower()
        return response in ['y', 'yes']
    
    return True

def create_users():
    """Create sample users"""
    created_users = []
    
    try:
        with transaction.atomic():
            print("👥 Creating sample users...")
            print("=" * 40)
            
            total_created = 0
            
            for role, users in SAMPLE_USERS.items():
                print(f"\n📝 Creating {role.title()}s:")
                
                for user_data in users:
                    try:
                        # Check if user already exists
                        if User.objects.filter(username=user_data['username']).exists():
                            print(f"   ⚠️  {user_data['username']} already exists - skipping")
                            continue
                        
                        if User.objects.filter(email=user_data['email']).exists():
                            print(f"   ⚠️  Email {user_data['email']} already exists - skipping")
                            continue
                        
                        # Create user
                        user = User.objects.create_user(
                            username=user_data['username'],
                            email=user_data['email'],
                            password=DEFAULT_PASSWORD,
                            first_name=user_data['first_name'],
                            last_name=user_data['last_name'],
                            role=user_data['role'],
                            is_active=True
                        )
                        
                        # Create authentication token
                        token, created = Token.objects.get_or_create(user=user)
                        
                        created_users.append(user)
                        total_created += 1
                        
                        print(f"   ✅ {user.first_name} {user.last_name} ({user.username}) - {user.email}")
                        
                    except Exception as e:
                        print(f"   ❌ Failed to create {user_data['username']}: {e}")
            
            print(f"\n🎉 Successfully created {total_created} users!")
            return created_users
            
    except Exception as e:
        print(f"❌ Error during user creation: {e}")
        import traceback
        traceback.print_exc()
        return []

def create_admin_user():
    """Optionally create an admin user"""
    print("\n🔧 Would you like to create an admin user?")
    response = input("Create admin user? (Y/n): ").strip().lower()
    
    if response not in ['n', 'no']:
        try:
            admin_username = "admin"
            admin_email = "admin@university.edu"
            
            # Check if admin already exists
            if User.objects.filter(username=admin_username).exists():
                print(f"   ⚠️  Admin user '{admin_username}' already exists")
                return
            
            if User.objects.filter(email=admin_email).exists():
                print(f"   ⚠️  Admin email '{admin_email}' already exists")
                return
            
            # Create admin user
            admin_user = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=DEFAULT_PASSWORD,
                first_name='System',
                last_name='Administrator',
                role='admin'
            )
            
            # Create token
            token, created = Token.objects.get_or_create(user=admin_user)
            
            print(f"✅ Admin user created!")
            print(f"   - Username: {admin_username}")
            print(f"   - Email: {admin_email}")
            print(f"   - Password: {DEFAULT_PASSWORD}")
            print(f"   - Role: admin")
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")

def display_summary():
    """Display summary of all users"""
    print("\n📊 Database Summary")
    print("=" * 40)
    
    total_users = User.objects.count()
    faculty_count = User.objects.filter(role='faculty').count()
    staff_count = User.objects.filter(role='staff').count()
    student_count = User.objects.filter(role='student').count()
    admin_count = User.objects.filter(role='admin').count()
    
    print(f"Total Users: {total_users}")
    print(f"   - Admins: {admin_count}")
    print(f"   - Faculty: {faculty_count}")
    print(f"   - Staff: {staff_count}")
    print(f"   - Students: {student_count}")
    
    print(f"\n🔑 Default password for all users: {DEFAULT_PASSWORD}")
    
    print("\n💡 Quick Test Accounts:")
    print("   Faculty: prof_johnson / johnson@university.edu")
    print("   Staff:   staff_anderson / anderson@university.edu")
    print("   Student: student_miller / miller@student.university.edu")
    if admin_count > 0:
        print("   Admin:   admin / admin@university.edu")

def main():
    """Main function"""
    print("🌱 Django User Management System - Database Population Tool")
    print("=" * 70)
    print()
    
    # Check if we're in the right directory
    if not (Path.cwd() / 'backend' / 'manage.py').exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   (The directory containing the 'backend' folder)")
        sys.exit(1)
    
    print("📋 This script will create:")
    print("   - 3 Faculty members")
    print("   - 3 Staff members")
    print("   - 5 Students")
    print("   - Optional: 1 Admin user")
    print(f"   - All with password: {DEFAULT_PASSWORD}")
    print()
    
    # Check existing users
    if not check_existing_users():
        print("❌ Operation cancelled by user")
        sys.exit(0)
    
    print("\n🚀 Starting user creation...")
    
    # Create users
    created_users = create_users()
    
    if created_users:
        # Optionally create admin
        create_admin_user()
        
        # Display summary
        display_summary()
        
        print("\n✨ Population completed!")
        print("\n📝 Next steps:")
        print("   1. Start the Django server: cd backend && python manage.py runserver")
        print("   2. Start the frontend: python frontend/main.py")
        print("   3. Test login with any of the created accounts")
        print(f"   4. Use password '{DEFAULT_PASSWORD}' for all accounts")
        
    else:
        print("❌ No users were created!")
        sys.exit(1)

if __name__ == '__main__':
    main()
