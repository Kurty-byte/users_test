"""
Frontend User Model

This module defines the User data model for the PyQt6 frontend application.
It represents user data received from the Django API and provides utility methods
for user role checking and data manipulation.

The User model is a dataclass that mirrors the backend User model structure
but is optimized for frontend operations and UI display.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class UserRole(Enum):
    """
    Enumeration of user roles in the system.
    
    These roles must match the backend UserRole choices and determine
    what actions and data each user can access in the frontend.
    """
    ADMIN = "admin"
    STUDENT = "student"
    FACULTY = "faculty"
    STAFF = "staff"


@dataclass
class User:
    """
    Frontend User model representing user data from Django API.
    
    This dataclass represents user information received from the backend API
    and provides convenience methods for role checking and data formatting.
    Authentication is handled entirely by the Django backend - this model
    only holds user profile information.
    
    Attributes:
        username (str): User's display name
        email (str): User's email address (used for authentication)
        role (UserRole): User's role in the system
        id (Optional[int]): Unique user identifier from database
        is_active (bool): Whether the user account is active
        first_name (Optional[str]): User's first name
        last_name (Optional[str]): User's last name
    
    Methods:
        from_api_data: Class method to create User from API response
        to_dict: Convert user to dictionary for API requests
        get_full_name: Get user's display name
        Role checking methods: is_admin, is_faculty, is_staff, is_student
        Permission checking methods: has_admin_privileges, can_view_users
    """
    username: str
    email: str
    role: UserRole = UserRole.STUDENT
    id: Optional[int] = None
    is_active: bool = True
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    @classmethod
    def from_api_data(cls, data: dict) -> 'User':
        """
        Create User instance from Django API response data.
        
        This method handles the conversion from JSON API response to a User object,
        including proper enum conversion for the role field.
        
        Args:
            data (dict): User data from API response
            
        Returns:
            User: New User instance with data from API
            
        Example:
            api_response = {
                'id': 1,
                'username': 'john_doe',
                'email': 'john@example.com',
                'role': 'student',
                'is_active': True
            }
            user = User.from_api_data(api_response)
        """
        return cls(
            id=data.get('id'),
            username=data.get('username', ''),
            email=data.get('email', ''),
            role=UserRole(data.get('role', 'student')),
            is_active=data.get('is_active', True),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
    
    def to_dict(self) -> dict:
        """
        Convert user to dictionary for API requests.
        
        Returns:
            dict: User data in dictionary format suitable for API requests
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'is_active': self.is_active,
            'first_name': self.first_name,
            'last_name': self.last_name
        }
    
    def get_full_name(self) -> str:
        """
        Get user's full display name.
        
        Returns the user's full name if both first and last names are available,
        otherwise returns the username as a fallback.
        
        Returns:
            str: Full name or username
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def is_admin(self) -> bool:
        """
        Check if user has admin role.
        
        Returns:
            bool: True if user is an admin, False otherwise
        """
        return self.role == UserRole.ADMIN
    
    def is_faculty(self) -> bool:
        """
        Check if user has faculty role.
        
        Returns:
            bool: True if user is faculty, False otherwise
        """
        return self.role == UserRole.FACULTY
    
    def is_staff(self) -> bool:
        """
        Check if user has staff role.
        
        Returns:
            bool: True if user is staff, False otherwise
        """
        return self.role == UserRole.STAFF
    
    def is_student(self) -> bool:
        """
        Check if user has student role.
        
        Returns:
            bool: True if user is a student, False otherwise
        """
        return self.role == UserRole.STUDENT
    
    def has_admin_privileges(self) -> bool:
        """
        Check if user has administrative privileges.
        
        Currently, both admin and faculty roles have elevated privileges
        for user management operations.
        
        Returns:
            bool: True if user has admin privileges, False otherwise
        """
        return self.role in [UserRole.ADMIN, UserRole.FACULTY]
    
    def can_view_users(self) -> bool:
        """
        Check if user can view other users based on role.
        
        Determines whether the user should have access to user listing
        and management features in the UI.
        
        Returns:
            bool: True if user can view other users, False otherwise
        """
        return self.role in [UserRole.ADMIN, UserRole.FACULTY, UserRole.STAFF]
    
    def get_accessible_roles(self) -> list[UserRole]:
        """
        Get list of roles this user can interact with or view.
        
        Based on the user's role, returns which other user roles they
        are allowed to see or manage in the system.
        
        Returns:
            list[UserRole]: List of accessible user roles
        """
        if self.role == UserRole.ADMIN:
            return list(UserRole)  # Admin can see all roles
        elif self.role == UserRole.FACULTY:
            return [UserRole.FACULTY, UserRole.STAFF, UserRole.STUDENT]
        elif self.role == UserRole.STAFF:
            return [UserRole.FACULTY]
        elif self.role == UserRole.STUDENT:
            return [UserRole.FACULTY, UserRole.STUDENT]
        else:
            return []
    
    def can_modify_user(self, target_user: 'User') -> bool:
        """
        Check if this user can modify another user's information.
        
        Args:
            target_user (User): The user to check modification permissions for
            
        Returns:
            bool: True if modifications are allowed, False otherwise
        """
        # Users can always modify themselves
        if self.id == target_user.id:
            return True
            
        # Admin can modify anyone
        if self.role == UserRole.ADMIN:
            return True
            
        # Faculty can modify students
        if self.role == UserRole.FACULTY and target_user.role == UserRole.STUDENT:
            return True
            
        return False