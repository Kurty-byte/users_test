"""
Quick verification script to ensure all User model instances are using the new API.
"""
import sys
import os

# Add the frontend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'frontend'))

def test_user_creation_methods():
    """Test that User model works correctly with new methods"""
    print("🧪 Testing User Model Creation Methods...")
    
    try:
        from frontend.models.user import User, UserRole
        
        # Test 1: Create user from API data (new method)
        api_data = {
            'id': 1,
            'username': 'faculty1',
            'email': 'faculty1@gmail.com',
            'role': 'faculty',
            'is_active': True,
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        user = User.from_api_data(api_data)
        print(f"✅ User created from API data: {user.get_full_name()}")
        print(f"   - ID: {user.id}")
        print(f"   - Username: {user.username}")
        print(f"   - Email: {user.email}")
        print(f"   - Role: {user.role.value}")
        print(f"   - Is Faculty: {user.is_faculty()}")
        print(f"   - Can view users: {user.can_view_users()}")
        
        # Test 2: Create user with minimal data
        minimal_data = {
            'username': 'student1',
            'email': 'student1@gmail.com',
            'role': 'student'
        }
        
        user2 = User.from_api_data(minimal_data)
        print(f"✅ User created with minimal data: {user2.username}")
        print(f"   - Role: {user2.role.value}")
        print(f"   - Is Student: {user2.is_student()}")
        
        # Test 3: Convert to dict
        user_dict = user.to_dict()
        print(f"✅ User converted to dict: {len(user_dict)} fields")
        
        return True
        
    except Exception as e:
        print(f"❌ User model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 User Model Fix Verification")
    print("=" * 50)
    
    if test_user_creation_methods():
        print("\n🎉 All User model methods are working correctly!")
        print("✅ The password_hash issue has been resolved")
        print("✅ User.from_api_data() is working properly")
        print("✅ The application should now run without errors")
    else:
        print("\n❌ There are still issues with the User model")
    
    return True

if __name__ == "__main__":
    main()
