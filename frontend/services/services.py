import requests
import logging
import time
import os
from typing import List, Optional, Dict, Any
from models.user import User, UserRole

# Load environment variables for frontend (optional since we have fallbacks)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, use defaults
    pass

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIConnectionError(Exception):
    """Custom exception for API connection issues"""
    pass


class APIAuthenticationError(Exception):
    """Custom exception for authentication issues"""
    pass


class DjangoAPIService:
    """Service to handle Django REST API communication"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('API_BASE_URL', 'http://127.0.0.1:8000/api')
        self.timeout = int(os.getenv('API_TIMEOUT', '10'))
        self.default_retries = int(os.getenv('API_RETRIES', '3'))
        self.token = None
        self.headers = {'Content-Type': 'application/json'}
        
        logger.info(f"DjangoAPIService initialized with base_url: {self.base_url}")
    
    def set_auth_token(self, token: str):
        """Set authentication token for API requests"""
        self.token = token
        self.headers['Authorization'] = f'Token {token}'
    
    def clear_auth_token(self):
        """Clear authentication token"""
        self.token = None
        if 'Authorization' in self.headers:
            del self.headers['Authorization']
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, retries: int = None) -> Dict[str, Any]:
        """Make HTTP request to Django API with retry logic"""
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
                    # Check if response has content and is JSON
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
                        return {
                            'success': True,
                            'data': {},
                            'status_code': response.status_code
                        }
                else:
                    # Try to parse error response as JSON
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
    """Enhanced user service that works with Django backend"""
    
    def __init__(self):
        self.api = DjangoAPIService()
        self.current_user: Optional[User] = None
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user with Django backend"""
        logger.info(f"Attempting login for user: {email}")
        
        response = self.api.make_request('POST', 'auth/login/', {
            'email': email,
            'password': password
        })
        
        if response['success']:
            user_data = response['data']['user']
            token = response['data']['token']
            
            # Set authentication token
            self.api.set_auth_token(token)
            
            # Create user object using the new from_api_data method
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
        """Logout current user"""
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
        """Register new user with Django backend"""
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
        """Get current user's profile from Django backend"""
        response = self.api.make_request('GET', 'auth/profile/')
        
        if response['success']:
            user_data = response['data']
            # Use the new from_api_data method
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
        """Update current user's profile"""
        data = {}
        if username:
            data['username'] = username
        if email:
            data['email'] = email
        if role:
            data['role'] = role.value
        
        response = self.api.make_request('PATCH', f'users/{self.current_user.id}/', data)
        
        if response['success']:
            # Update current user object
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
        """Change user password"""
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
        """Get available user roles from Django backend"""
        response = self.api.make_request('GET', 'roles/')
        
        if response['success']:
            return response['data']['roles']
        
        # Fallback to local roles if API is unavailable
        return [
            {'value': role.value, 'label': role.value.title()}
            for role in UserRole
        ]
    
    def get_all_users(self) -> Dict[str, Any]:
        """Get all users (admin only)"""
        response = self.api.make_request('GET', 'users/')
        
        if response['success']:
            users = []
            # Handle paginated response - extract results array
            users_data = response['data'].get('results', response['data'])
            
            # If it's still not a list, make it one
            if not isinstance(users_data, list):
                users_data = [users_data]
            
            for user_data in users_data:
                # Use the new from_api_data method instead of direct constructor
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
        """Toggle user active status (admin only)"""
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
        """Change user role (admin only)"""
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
        """Get available filter roles based on current user's permissions"""
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


# Legacy UserService for backward compatibility - file-based methods removed
# All user operations now use Django API exclusively
