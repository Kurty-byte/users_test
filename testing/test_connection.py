#!/usr/bin/env python3
"""
Simple script to test Django backend connection
"""
import requests
import sys

def test_django_connection():
    """Test if Django backend is running and accessible"""
    try:
        response = requests.get('http://127.0.0.1:8000/admin/', timeout=5)
        if response.status_code in [200, 302]:  # 302 is redirect to login
            print("✅ Django backend is running!")
            return True
        else:
            print(f"❌ Django backend responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Django backend is not running or not accessible at http://127.0.0.1:8000")
        print("Please start the Django server with: python manage.py runserver")
        return False
    except requests.exceptions.Timeout:
        print("❌ Connection to Django backend timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def test_api_endpoints():
    """Test specific API endpoints"""
    base_url = "http://127.0.0.1:8000/api"
    endpoints = [
        "/auth/login/",
        "/users/",
        "/roles/"
    ]
    
    print("\nTesting API endpoints:")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code < 500:
                print(f"✅ {endpoint} - Available (Status: {response.status_code})")
            else:
                print(f"⚠️  {endpoint} - Server Error (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {endpoint} - Connection failed: {e}")

if __name__ == "__main__":
    print("Testing Django Backend Connection...")
    print("=" * 50)
    
    if test_django_connection():
        test_api_endpoints()
        print("\n✅ Backend tests completed!")
    else:
        print("\n❌ Backend is not accessible. Please start Django server first.")
        print("\nTo start Django server:")
        print("1. cd backend")
        print("2. python manage.py runserver")
        sys.exit(1)
