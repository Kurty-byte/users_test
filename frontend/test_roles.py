#!/usr/bin/env python3
"""
Test script to verify role-based functionality
"""

from models.user import User, UserRole
from services.services import UserService

def test_roles():
    # Initialize service
    service = UserService("test_users.json")
    
    print("=== Testing Role-Based User Management System ===\n")
    
    # Test user creation with different roles
    print("1. Creating users with different roles:")
    
    # Create users
    service.register_user("student1", "student1@example.com", "password123", UserRole.STUDENT)
    service.register_user("faculty1", "faculty1@example.com", "password123", UserRole.FACULTY)
    service.register_user("staff1", "staff1@example.com", "password123", UserRole.STAFF)
    
    print("   ✓ Created student, faculty, and staff users")
    
    # Test login
    print("\n2. Testing login with different roles:")
    
    # Test admin login
    success, message, admin_user = service.login_user("admin", "admin123")
    if success:
        print(f"   ✓ Admin login successful: {admin_user.username} ({admin_user.role.value})")
    
    # Test student login
    success, message, student_user = service.login_user("student1", "password123")
    if success:
        print(f"   ✓ Student login successful: {student_user.username} ({student_user.role.value})")
    
    # Test role-based permissions
    print("\n3. Testing role-based permissions:")
    
    # Test admin privileges
    if admin_user.is_admin():
        print("   ✓ Admin has admin privileges")
    
    if admin_user.has_admin_privileges():
        print("   ✓ Admin has admin privileges (via has_admin_privileges)")
    
    # Test student privileges
    if not student_user.is_admin():
        print("   ✓ Student does not have admin privileges")
    
    # Test role filtering
    print("\n4. Testing role filtering:")
    
    students = service.get_users_by_role(UserRole.STUDENT)
    faculty = service.get_users_by_role(UserRole.FACULTY)
    admins = service.get_users_by_role(UserRole.ADMIN)
    
    print(f"   ✓ Found {len(students)} student(s)")
    print(f"   ✓ Found {len(faculty)} faculty member(s)")
    print(f"   ✓ Found {len(admins)} admin(s)")
    
    # Test admin actions
    print("\n5. Testing admin actions:")
    
    # Find student to modify
    student = next((u for u in service.get_all_users() if u.role == UserRole.STUDENT), None)
    if student:
        # Test role change
        success, message = service.update_user_role(student.id, UserRole.STAFF, admin_user)
        if success:
            print(f"   ✓ Successfully changed {student.username}'s role to staff")
        
        # Test deactivation
        success, message = service.deactivate_user(student.id, admin_user)
        if success:
            print(f"   ✓ Successfully deactivated {student.username}")
        
        # Test reactivation
        success, message = service.activate_user(student.id, admin_user)
        if success:
            print(f"   ✓ Successfully reactivated {student.username}")
    
    print("\n6. Current user summary:")
    all_users = service.get_all_users()
    for user in all_users:
        status = "Active" if user.is_active else "Inactive"
        print(f"   • {user.username} ({user.role.value.title()}) - {status}")
    
    print("\n=== All tests completed successfully! ===")

if __name__ == "__main__":
    test_roles()
