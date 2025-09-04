"""
Django User Models

This module defines the custom User model and role system for the user management application.
It extends Django's AbstractUser to provide role-based access control and email-based authentication.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class UserRole(models.TextChoices):
    """
    Enumeration of available user roles in the system.
    
    Each role has different permissions and access levels:
    - ADMIN: Full system access, can manage all users and roles
    - FACULTY: Can view and manage students, limited administrative access
    - STAFF: Limited access, can view faculty information
    - STUDENT: Basic access, can view faculty and other students
    """
    ADMIN = 'admin', 'Admin'
    STUDENT = 'student', 'Student'
    FACULTY = 'faculty', 'Faculty'
    STAFF = 'staff', 'Staff'


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    This model replaces the default Django User model and provides:
    - Email-based authentication instead of username
    - Role-based access control
    - Automatic timestamp tracking
    - Enhanced user profile capabilities
    
    Attributes:
        email (EmailField): Unique email address used for authentication
        role (CharField): User's role in the system (admin, faculty, staff, student)
        is_active (BooleanField): Whether the user account is active
        created_at (DateTimeField): Timestamp when the user was created
        updated_at (DateTimeField): Timestamp when the user was last updated
    
    Meta:
        - Uses 'email' as the primary authentication field
        - Requires 'username' as an additional required field
        - Stores data in 'users' table
    """
    
    email = models.EmailField(
        unique=True,
        help_text="User's email address - used for authentication"
    )
    
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
        help_text="User's role in the system - determines access permissions"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the user account was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the user account was last updated"
    )

    # Use email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']  # Order by creation date, newest first

    def __str__(self):
        """
        String representation of the User object.
        
        Returns:
            str: Username and email in format "username (email@domain.com)"
        """
        return f"{self.username} ({self.email})"
    
    def get_role_display_name(self):
        """
        Get the human-readable display name for the user's role.
        
        Returns:
            str: Capitalized role name (e.g., "Admin", "Student")
        """
        return self.get_role_display()
    
    def has_admin_privileges(self):
        """
        Check if the user has administrative privileges.
        
        Returns:
            bool: True if user is admin or has staff status, False otherwise
        """
        return self.role == UserRole.ADMIN or self.is_staff
    
    def can_manage_users(self):
        """
        Check if the user can manage other users based on their role.
        
        Returns:
            bool: True if user can manage others (admin/faculty), False otherwise
        """
        return self.role in [UserRole.ADMIN, UserRole.FACULTY]
    
    def get_manageable_roles(self):
        """
        Get list of roles this user can assign to others.
        
        Returns:
            list: List of UserRole choices the user can assign
        """
        if self.role == UserRole.ADMIN:
            return list(UserRole.choices)
        elif self.role == UserRole.FACULTY:
            return [
                (UserRole.FACULTY, 'Faculty'),
                (UserRole.STAFF, 'Staff'),
                (UserRole.STUDENT, 'Student')
            ]
        else:
            return []
