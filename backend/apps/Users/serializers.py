"""
Django REST Framework Serializers for User Management

This module contains serializers that handle the conversion between Django model instances
and Python data types for JSON serialization/deserialization. Each serializer is responsible
for validating input data and transforming it appropriately for the User model.

Serializers included:
- UserSerializer: Basic user data serialization for API responses
- UserCreateSerializer: User registration with password validation
- UserLoginSerializer: Authentication credential validation
- UserUpdateSerializer: User profile update validation
- PasswordChangeSerializer: Password change with security validation
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserRole


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User objects - used for API responses.
    
    This serializer handles the basic representation of user data that is safe
    to expose in API responses. It excludes sensitive information like passwords
    and includes only essential user information.
    
    Fields:
        - id: Unique user identifier
        - username: User's display name
        - email: User's email address
        - role: User's role in the system
        - is_active: Whether the user account is active
        - created_at: Account creation timestamp
        - updated_at: Last update timestamp
    """
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users (registration).
    
    This serializer handles user registration with comprehensive validation:
    - Password strength validation using Django's built-in validators
    - Password confirmation matching
    - Email uniqueness validation
    - Role assignment with default to STUDENT
    
    Fields:
        - username: Desired username (required)
        - email: Email address for authentication (required)
        - password: Password (write-only, validated)
        - password_confirm: Password confirmation (write-only)
        - role: User role (optional, defaults to STUDENT)
    """
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password],
        help_text="Password must meet Django's password requirements"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Must match the password field"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'role']
        extra_kwargs = {
            'email': {'help_text': 'Email address used for login'},
            'role': {'help_text': 'User role - defaults to student'}
        }
        
    def validate(self, attrs):
        """
        Validate that passwords match.
        
        Args:
            attrs (dict): Serializer data attributes
            
        Returns:
            dict: Validated attributes
            
        Raises:
            serializers.ValidationError: If passwords don't match
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        """
        Create a new user with validated data.
        
        Args:
            validated_data (dict): Validated user data
            
        Returns:
            User: Created user instance
        """
        # Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Create user instance
        user = User.objects.create_user(**validated_data)
        user.set_password(password)  # Properly hash the password
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user authentication.
    
    This serializer validates login credentials and returns the authenticated
    user object if credentials are valid. It uses email-based authentication
    as configured in the User model.
    
    Fields:
        - email: User's email address
        - password: User's password (write-only)
    """
    email = serializers.EmailField(
        help_text="Email address used for registration"
    )
    password = serializers.CharField(
        write_only=True,
        help_text="User's password"
    )
    
    def validate(self, attrs):
        """
        Validate user credentials and return authenticated user.
        
        Args:
            attrs (dict): Login credentials
            
        Returns:
            dict: Validated attributes with user object
            
        Raises:
            serializers.ValidationError: If credentials are invalid or account is disabled
        """
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Authenticate using email as username
            user = authenticate(username=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
                
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information.
    
    This serializer handles profile updates with validation to ensure
    data integrity, particularly for email uniqueness checks.
    
    Fields:
        - username: Updated username
        - email: Updated email address
        - role: Updated user role
    """
    
    class Meta:
        model = User
        fields = ['username', 'email', 'role']
        
    def validate_email(self, value):
        """
        Validate that email is unique among other users.
        
        Args:
            value (str): Email address to validate
            
        Returns:
            str: Validated email address
            
        Raises:
            serializers.ValidationError: If email already exists for another user
        """
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user passwords.
    
    This serializer handles password changes with security validation:
    - Verifies current password before allowing change
    - Validates new password strength
    - Ensures new password confirmation matches
    
    Fields:
        - old_password: Current password for verification (write-only)
        - new_password: New password (write-only, validated)
        - new_password_confirm: New password confirmation (write-only)
    """
    old_password = serializers.CharField(
        write_only=True,
        help_text="Current password for verification"
    )
    new_password = serializers.CharField(
        write_only=True, 
        validators=[validate_password],
        help_text="New password meeting security requirements"
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        help_text="Must match new_password field"
    )
    
    def validate_old_password(self, value):
        """
        Validate that the old password is correct.
        
        Args:
            value (str): Current password provided by user
            
        Returns:
            str: Validated old password
            
        Raises:
            serializers.ValidationError: If old password is incorrect
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    def validate(self, attrs):
        """
        Validate that new passwords match.
        
        Args:
            attrs (dict): Password change data
            
        Returns:
            dict: Validated attributes
            
        Raises:
            serializers.ValidationError: If new passwords don't match
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def save(self):
        """
        Save the new password for the current user.
        
        Returns:
            User: Updated user instance
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
