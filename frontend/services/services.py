"""
Frontend API Services

This module provides comprehensive API communication services for the PyQt6 frontend
to interact with the Django REST API backend. It implements robust error handling,
authentication management, and retry logic for reliable API communication.

Classes:
    APIConnectionError: Custom exception for API connection issues
    APIAuthenticationError: Custom exception for authentication issues  
    DjangoAPIService: Low-level API communication service
    UserService: High-level user management service

The service layer handles:
- HTTP request/response management
- Token-based authentication
- Automatic retry logic with exponential backoff
- Error handling and logging
- User session management
- Role-based API operations
"""

import requests
import logging
import time
import os
from typing import List, Optional, Dict, Any
from models.user import User, UserRole

# Load environment variables for frontend configuration
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, use defaults
    pass

# Configure logging for API service operations
log_level = os.getenv('LOG_LEVEL', 'INFO')

# Create logs directory if it doesn't exist
import pathlib
log_dir = pathlib.Path(__file__).parent.parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

# Configure logging with both console and file output
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # Console handler (existing behavior)
        logging.StreamHandler(),
        # File handler (new - saves to logs/frontend.log)
        logging.FileHandler(log_dir / 'frontend.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)


class APIConnectionError(Exception):
    """
    Custom exception for API connection issues.
    
    Raised when the frontend cannot establish a connection to the Django API,
    including network errors, timeouts, and server unavailability.
    """
    pass


class APIAuthenticationError(Exception):
    """
    Custom exception for authentication issues.
    
    Raised when API requests fail due to authentication problems,
    including invalid tokens, expired sessions, and insufficient permissions.
    """
    pass


class DjangoAPIService:
    """
    Low-level service for Django REST API communication.
    
    This service handles the fundamental HTTP communication with the Django backend,
    including authentication token management, request retry logic, and response
    processing. It provides a robust foundation for higher-level services.
    
    Attributes:
        base_url (str): Base URL for the Django API
        timeout (int): Request timeout in seconds
        default_retries (int): Number of retry attempts for failed requests
        token (str): Authentication token for API requests
        headers (dict): HTTP headers including Content-Type and Authorization
    
    Environment Variables:
        API_BASE_URL: Base URL for Django API (default: http://127.0.0.1:8000/api)
        API_TIMEOUT: Request timeout in seconds (default: 10)
        API_RETRIES: Number of retry attempts (default: 3)
        LOG_LEVEL: Logging level (default: INFO)
    """
    
    def __init__(self, base_url: str = None):
        """
        Initialize the Django API service.
        
        Args:
            base_url (str, optional): Override default API base URL
        """
        self.base_url = base_url or os.getenv('API_BASE_URL', 'http://127.0.0.1:8000/api')
        self.timeout = int(os.getenv('API_TIMEOUT', '10'))
        self.default_retries = int(os.getenv('API_RETRIES', '3'))
        self.token = None
        self.headers = {'Content-Type': 'application/json'}
        
        logger.info(f"DjangoAPIService initialized with base_url: {self.base_url}")
    
    def set_auth_token(self, token: str):
        """
        Set authentication token for API requests.
        
        Args:
            token (str): Authentication token from login response
        """
        self.token = token
        self.headers['Authorization'] = f'Token {token}'
        logger.debug("Authentication token set")
    
    def clear_auth_token(self):
        """
        Clear authentication token and remove Authorization header.
        
        Called during logout to ensure subsequent requests are unauthenticated.
        """
        self.token = None
        if 'Authorization' in self.headers:
            del self.headers['Authorization']
        logger.debug("Authentication token cleared")
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, retries: int = None) -> Dict[str, Any]:
        """
        Make HTTP request to Django API with comprehensive error handling.
        
        This method implements retry logic for transient failures and provides
        detailed error reporting for debugging and user feedback.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint (str): API endpoint relative to base_url
            data (Optional[Dict]): Request payload for POST/PUT/PATCH requests
            retries (int, optional): Override default retry count
            
        Returns:
            Dict[str, Any]: Standardized response dictionary with:
                - success (bool): Whether the request succeeded
                - data (dict): Response data for successful requests
                - error (dict): Error details for failed requests
                - status_code (int): HTTP status code
                
        Example:
            response = api.make_request('POST', 'auth/login/', {
                'email': 'user@example.com',
                'password': 'password123'
            })
            
            if response['success']:
                user_data = response['data']['user']
                token = response['data']['token']
            else:
                error_message = response['error']['detail']
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        retries = retries or self.default_retries
        
        for attempt in range(retries):
            try:
                logger.info(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data if data else None,
                    timeout=self.timeout
                )
                
                logger.info(f"Response status: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    # Success responses
                    if response.content:
                        try:
                            response_data = response.json()
                            logger.debug(f"Response data: {response_data}")
                            return {
                                'success': True,
                                'data': response_data,
                                'status_code': response.status_code
                            }
                        except ValueError as e:
                            logger.error(f"Failed to parse JSON response: {e}")
                            return {
                                'success': False,
                                'error': {'detail': 'Server returned invalid JSON response'},
                                'status_code': response.status_code
                            }
                    else:
                        # Empty response for DELETE operations
                        return {
                            'success': True,
                            'data': {},
                            'status_code': response.status_code
                        }
                else:
                    # Error responses (4xx, 5xx)
                    try:
                        error_data = response.json() if response.content else {'detail': 'Unknown error'}
                    except ValueError:
                        # If not JSON, it's likely an HTML error page
                        error_data = {'detail': f'Server error (Status: {response.status_code})'}
                    
                    logger.warning(f"API error: {error_data}")
                    return {
                        'success': False,
                        'error': error_data,
                        'status_code': response.status_code
                    }
                    
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    time.sleep(1)  # Wait 1 second before retry
                    continue
                else:
                    logger.error(f"All connection attempts failed: {e}")
                    return {
                        'success': False,
                        'error': {'detail': f'Connection error: Unable to connect to server'},
                        'status_code': 0
                    }
            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                else:
                    logger.error(f"Request timeout after {retries} attempts: {e}")
                    return {
                        'success': False,
                        'error': {'detail': f'Request timeout: Server is not responding'},
                        'status_code': 0
                    }
            except requests.exceptions.RequestException as e:
                logger.error(f"Unexpected request error: {e}")
                return {
                    'success': False,
                    'error': {'detail': f'Network error: {str(e)}'},
                    'status_code': 0
                }
        
        # This should never be reached, but just in case
        return {
            'success': False,
            'error': {'detail': 'Unexpected error occurred'},
            'status_code': 0
        }


class UserService:
    """
    High-level user management service for Django backend integration.
    
    This service provides a clean interface for all user-related operations,
    abstracting the complexity of API communication and providing convenient
    methods for authentication, user management, and role-based operations.
    
    The service maintains the current user session and handles token-based
    authentication automatically for subsequent requests.
    
    Attributes:
        api (DjangoAPIService): Low-level API communication service
        current_user (Optional[User]): Currently authenticated user object
        
    Key Methods:
        Authentication: login, logout, register, change_password
        User Management: get_all_users, toggle_user_status, change_user_role
        Profile: get_current_user_profile, update_user_profile
        Roles: get_available_roles, get_available_filter_roles
    """
    
    def __init__(self):
        """
        Initialize the user service with Django API backend.
        """
        self.api = DjangoAPIService()
        self.current_user: Optional[User] = None
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with Django backend.
        
        Sends login credentials to the Django API and, if successful,
        stores the authentication token and user information for
        subsequent requests.
        
        Args:
            email (str): User's email address
            password (str): User's password
            
        Returns:
            Dict[str, Any]: Login result with:
                - success (bool): Whether login succeeded
                - user (User): User object if successful
                - token (str): Authentication token if successful
                - message (str): Success message if successful
                - error (str): Error message if failed
                
        Example:
            result = user_service.login('user@example.com', 'password123')
            if result['success']:
                current_user = result['user']
                print(f"Welcome, {current_user.username}!")
            else:
                print(f"Login failed: {result['error']}")
        """
        logger.info(f"Attempting login for user: {email}")
        
        response = self.api.make_request('POST', 'auth/login/', {
            'email': email,
            'password': password
        })
        
        if response['success']:
            user_data = response['data']['user']
            token = response['data']['token']
            
            # Set authentication token for subsequent requests
            self.api.set_auth_token(token)
            
            # Create user object from API response
            self.current_user = User.from_api_data(user_data)
            
            logger.info(f"Login successful for user: {self.current_user.username}")
            return {
                'success': True,
                'user': self.current_user,
                'token': token,
                'message': response['data'].get('message', 'Login successful')
            }
        
        logger.warning(f"Login failed for user: {email}")
        return {
            'success': False,
            'error': response['error'].get('detail', 'Login failed')
        }
    
    def logout(self) -> Dict[str, Any]:
        """
        Logout current user and invalidate authentication token.
        
        Calls the Django logout endpoint to invalidate the server-side token
        and clears the local authentication state.
        
        Returns:
            Dict[str, Any]: Logout result with success status and message
        """
        logger.info("Attempting logout")
        
        if self.api.token:
            response = self.api.make_request('POST', 'auth/logout/')
            self.api.clear_auth_token()
            self.current_user = None
            
            logger.info("Logout successful")
            return {
                'success': True,
                'message': 'Logged out successfully'
            }
        
        logger.warning("Logout attempted but no user logged in")
        return {
            'success': False,
            'error': 'No user logged in'
        }
    
    def register(self, username: str, email: str, password: str, password_confirm: str, role: UserRole = UserRole.STUDENT) -> Dict[str, Any]:
        """
        Register new user with Django backend.
        
        Creates a new user account with the provided information. The registration
        does not automatically log in the user - a separate login is required.
        
        Args:
            username (str): Desired username
            email (str): User's email address (used for login)
            password (str): User's password
            password_confirm (str): Password confirmation
            role (UserRole): User's role (defaults to STUDENT)
            
        Returns:
            Dict[str, Any]: Registration result with success status and user data or errors
        """
        response = self.api.make_request('POST', 'users/', {
            'username': username,
            'email': email,
            'password': password,
            'password_confirm': password_confirm,
            'role': role.value
        })
        
        if response['success']:
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': response['data']
            }
        
        return {
            'success': False,
            'error': response['error']
        }
    
    def get_current_user_profile(self) -> Dict[str, Any]:
        """
        Get current user's profile from Django backend.
        
        Fetches the latest profile information for the authenticated user
        and updates the local user object.
        
        Returns:
            Dict[str, Any]: Profile result with user data or error
        """
        response = self.api.make_request('GET', 'auth/profile/')
        
        if response['success']:
            user_data = response['data']
            self.current_user = User.from_api_data(user_data)
            
            return {
                'success': True,
                'user': self.current_user
            }
        
        return {
            'success': False,
            'error': response['error'].get('detail', 'Failed to get profile')
        }
    
    def update_user_profile(self, username: str = None, email: str = None, role: UserRole = None) -> Dict[str, Any]:
        """
        Update current user's profile information.
        
        Args:
            username (str, optional): New username
            email (str, optional): New email address
            role (UserRole, optional): New role (admin required for role changes)
            
        Returns:
            Dict[str, Any]: Update result with success status and updated user data
        """
        data = {}
        if username:
            data['username'] = username
        if email:
            data['email'] = email
        if role:
            data['role'] = role.value
        
        response = self.api.make_request('PATCH', f'users/{self.current_user.id}/', data)
        
        if response['success']:
            # Update local user object
            if self.current_user:
                if username:
                    self.current_user.username = username
                if email:
                    self.current_user.email = email
                if role:
                    self.current_user.role = role
            
            return {
                'success': True,
                'message': 'Profile updated successfully',
                'user': self.current_user
            }
        
        return {
            'success': False,
            'error': response['error']
        }
    
    def change_password(self, old_password: str, new_password: str, new_password_confirm: str) -> Dict[str, Any]:
        """
        Change user password with verification.
        
        Args:
            old_password (str): Current password for verification
            new_password (str): New password
            new_password_confirm (str): Confirmation of new password
            
        Returns:
            Dict[str, Any]: Password change result with success status and message
        """
        response = self.api.make_request('POST', 'auth/change-password/', {
            'old_password': old_password,
            'new_password': new_password,
            'new_password_confirm': new_password_confirm
        })
        
        if response['success']:
            return {
                'success': True,
                'message': response['data']['message']
            }
        
        return {
            'success': False,
            'error': response['error']
        }
    
    def get_available_roles(self) -> List[Dict[str, str]]:
        """
        Get available user roles from Django backend.
        
        Returns a list of roles that the current user can assign to others,
        based on their own role and permissions.
        
        Returns:
            List[Dict[str, str]]: List of role dictionaries with 'value' and 'label' keys
        """
        response = self.api.make_request('GET', 'roles/')
        
        if response['success']:
            return response['data']['roles']
        
        # Fallback to local roles if API is unavailable
        return [
            {'value': role.value, 'label': role.value.title()}
            for role in UserRole
        ]
    
    def get_all_users(self) -> Dict[str, Any]:
        """
        Get all users based on current user's permissions.
        
        Returns a filtered list of users that the current user is allowed
        to view based on their role and the system's access control rules.
        
        Returns:
            Dict[str, Any]: Result with list of User objects or error
        """
        response = self.api.make_request('GET', 'users/')
        
        if response['success']:
            users = []
            # Handle paginated response - extract results array
            users_data = response['data'].get('results', response['data'])
            
            # If it's still not a list, make it one
            if not isinstance(users_data, list):
                users_data = [users_data]
            
            for user_data in users_data:
                user = User.from_api_data(user_data)
                users.append(user)
            
            return {
                'success': True,
                'users': users
            }
        
        return {
            'success': False,
            'error': response['error'].get('detail', 'Failed to get users')
        }

    def toggle_user_status(self, user_id: int) -> Dict[str, Any]:
        """
        Toggle user active status (role-based permissions apply).
        
        Args:
            user_id (int): ID of the user whose status should be toggled
            
        Returns:
            Dict[str, Any]: Result with updated user data or error
        """
        response = self.api.make_request('PATCH', f'users/{user_id}/toggle-status/')
        
        if response['success']:
            return {
                'success': True,
                'user': response['data']['user'],
                'message': response['data']['message']
            }
        
        return {
            'success': False,
            'error': response['error'].get('detail', 'Failed to toggle user status')
        }
    
    def change_user_role(self, user_id: int, new_role: str) -> Dict[str, Any]:
        """
        Change user role (admin only).
        
        Args:
            user_id (int): ID of the user whose role should be changed
            new_role (str): New role value
            
        Returns:
            Dict[str, Any]: Result with updated user data or error
        """
        response = self.api.make_request('PATCH', f'users/{user_id}/change-role/', {
            'role': new_role
        })
        
        if response['success']:
            return {
                'success': True,
                'user': response['data']['user'],
                'message': response['data']['message']
            }
        
        return {
            'success': False,
            'error': response['error'].get('detail', 'Failed to change user role')
        }
    
    def get_available_filter_roles(self) -> Dict[str, Any]:
        """
        Get available filter roles based on current user's permissions.
        
        Returns role options that can be used to filter user lists in the UI.
        
        Returns:
            Dict[str, Any]: Result with filter roles list or error
        """
        response = self.api.make_request('GET', 'filter-roles/')
        
        if response['success']:
            return {
                'success': True,
                'filter_roles': response['data']['filter_roles']
            }
        
        return {
            'success': False,
            'error': response['error'].get('detail', 'Failed to get filter roles')
        }


# Note: All user operations now use Django API exclusively
# Legacy file-based methods have been removed in favor of centralized backend management
