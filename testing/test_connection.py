#!/usr/bin/env python3
"""
Django Backend Connection Test Utility

This script provides a comprehensive test suite for verifying that the Django
backend is running and accessible. It performs connectivity tests and validates
API endpoint availability to ensure the backend is properly configured.

Functions:
    test_django_connection: Test basic Django server connectivity
    test_api_endpoints: Test specific API endpoints for availability
    main: Run all tests and provide detailed status report

Usage:
    python test_connection.py

This utility should be run before starting the frontend application to ensure
the backend is ready to handle API requests.
"""

import requests
import sys


def test_django_connection():
    """
    Test if Django backend is running and accessible.
    
    Attempts to connect to the Django admin interface as a basic connectivity
    test. The admin interface should be available even without authentication.
    
    Returns:
        bool: True if Django backend is accessible, False otherwise
        
    Status Codes:
        - 200: Admin page loaded successfully
        - 302: Redirect to login (expected behavior, indicates server is running)
        - Other: Server issue or not running
    """
    try:
        print("🔍 Testing Django backend connectivity...")
        response = requests.get('http://127.0.0.1:8000/admin/', timeout=5)
        
        if response.status_code in [200, 302]:  # 302 is redirect to login
            print("✅ Django backend is running and accessible!")
            print(f"   Server responded with status code: {response.status_code}")
            return True
        else:
            print(f"❌ Django backend responded with unexpected status code: {response.status_code}")
            print("   This may indicate a server configuration issue.")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Django backend is not running or not accessible at http://127.0.0.1:8000")
        print("   Please start the Django server with: python manage.py runserver")
        return False
    except requests.exceptions.Timeout:
        print("❌ Connection to Django backend timed out")
        print("   The server may be overloaded or experiencing issues.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error testing connection: {e}")
        return False


def test_api_endpoints():
    """
    Test specific API endpoints for availability and proper response.
    
    Tests key API endpoints that the frontend application depends on.
    This helps identify specific issues with API configuration or routing.
    
    Endpoints Tested:
        - /api/auth/login/ - Authentication endpoint
        - /api/users/ - User management endpoint
        - /api/roles/ - Role management endpoint
        
    Note: These tests only verify endpoint availability, not authentication
    or business logic functionality.
    """
    base_url = "http://127.0.0.1:8000/api"
    endpoints = [
        ("/auth/login/", "User authentication"),
        ("/users/", "User management"),
        ("/roles/", "Role management")
    ]
    
    print("\n🔍 Testing API endpoints...")
    all_endpoints_ok = True
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code < 500:
                # Any response below 500 indicates the endpoint exists
                status_icon = "✅" if response.status_code < 400 else "⚠️"
                print(f"   {status_icon} {endpoint} ({description}) - Status: {response.status_code}")
                
                if response.status_code == 401:
                    print(f"      Note: Authentication required (expected for protected endpoints)")
                elif response.status_code == 405:
                    print(f"      Note: Method not allowed (endpoint exists but wrong HTTP method)")
            else:
                print(f"   ❌ {endpoint} ({description}) - Server Error: {response.status_code}")
                all_endpoints_ok = False
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ {endpoint} ({description}) - Connection failed")
            all_endpoints_ok = False
        except requests.exceptions.Timeout:
            print(f"   ❌ {endpoint} ({description}) - Request timeout")
            all_endpoints_ok = False
        except Exception as e:
            print(f"   ❌ {endpoint} ({description}) - Error: {e}")
            all_endpoints_ok = False
    
    if all_endpoints_ok:
        print("\n✅ All API endpoints are responsive!")
    else:
        print("\n⚠️  Some API endpoints have issues. Check Django configuration.")
    
    return all_endpoints_ok


def main():
    """
    Run comprehensive backend connectivity tests.
    
    Executes all test functions and provides a summary report of the
    Django backend status. Exits with appropriate status codes for
    automation and scripting purposes.
    
    Exit Codes:
        0: All tests passed - backend is ready
        1: Some tests failed - backend has issues
    """
    print("=" * 60)
    print("Django Backend Connection Test")
    print("=" * 60)
    
    # Test basic connectivity
    connection_ok = test_django_connection()
    
    # Test API endpoints if basic connection works
    api_ok = True
    if connection_ok:
        api_ok = test_api_endpoints()
    else:
        print("\n⚠️  Skipping API endpoint tests due to connection failure.")
    
    # Summary report
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"  Django Server: {'✅ Running' if connection_ok else '❌ Not accessible'}")
    print(f"  API Endpoints: {'✅ Available' if api_ok else '❌ Issues detected'}")
    
    if connection_ok and api_ok:
        print("\n🎉 Backend is ready! You can start the frontend application.")
        sys.exit(0)
    else:
        print("\n🔧 Backend issues detected. Please resolve before using the application.")
        print("\nTroubleshooting steps:")
        print("  1. Ensure Django server is running: python manage.py runserver")
        print("  2. Check for database migrations: python manage.py migrate")
        print("  3. Verify settings.py configuration")
        print("  4. Check for any error messages in Django console")
        sys.exit(1)


if __name__ == "__main__":
    main()
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
