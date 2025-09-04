from dataclasses import dataclass
from typing import Optional
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    STUDENT = "student"
    FACULTY = "faculty"
    STAFF = "staff"

@dataclass
class User:
    """
    Frontend User model - represents user data received from Django API.
    Authentication is handled by Django backend, not this frontend model.
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
        """Create User instance from API response data"""
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
        """Convert user to dictionary for API requests"""
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
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.role == UserRole.ADMIN
    
    def is_faculty(self) -> bool:
        """Check if user is faculty"""
        return self.role == UserRole.FACULTY
    
    def is_staff(self) -> bool:
        """Check if user is staff"""
        return self.role == UserRole.STAFF
    
    def is_student(self) -> bool:
        """Check if user is a student"""
        return self.role == UserRole.STUDENT
    
    def has_admin_privileges(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in [UserRole.ADMIN, UserRole.FACULTY]
    
    def can_view_users(self) -> bool:
        """Check if user can view other users based on role"""
        return self.role in [UserRole.ADMIN, UserRole.FACULTY, UserRole.STAFF]