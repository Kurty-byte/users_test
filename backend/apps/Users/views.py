"""
Django REST API Views for User Management

This module contains all the API view classes and functions that handle HTTP requests
for user management operations. It implements role-based access control and provides
endpoints for authentication, user CRUD operations, and administrative functions.

The views follow RESTful principles and use Django REST Framework's class-based views
and function-based views with appropriate permissions and serializers.

Key Features:
- Role-based access control with custom permissions
- Token-based authentication
- Comprehensive user management operations
- Security validations and error handling
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import User
from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    UserLoginSerializer, 
    UserUpdateSerializer,
    PasswordChangeSerializer
)


class IsAdminOrCreateOnly(permissions.BasePermission):
    """
    Custom permission class for user list/create operations.
    
    This permission allows:
    - Anyone to create users (public registration)
    - Only authenticated users to view user lists (filtered by role)
    
    The actual filtering of visible users is handled in the view's get_queryset method
    based on the user's role and permissions.
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to access the view.
        
        Args:
            request: HTTP request object
            view: The view being accessed
            
        Returns:
            bool: True if permission granted, False otherwise
        """
        if request.method == 'POST':
            return True  # Allow public registration
        # For GET requests, require authentication
        return request.user.is_authenticated


class UserListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating users.
    
    GET: List users based on role-based permissions
    POST: Create a new user (public registration)
    
    The queryset is dynamically filtered based on the requesting user's role:
    - Admin: Can see all users
    - Faculty: Can see faculty, staff, and students (not admins)
    - Staff: Can only see faculty
    - Student: Can see faculty and other students
    
    Endpoints:
        GET /api/users/ - List users (requires authentication)
        POST /api/users/ - Create new user (public access)
    """
    permission_classes = [IsAdminOrCreateOnly]
    
    def get_queryset(self):
        """
        Filter users based on current user's role and permissions.
        
        Returns:
            QuerySet: Filtered user queryset based on role permissions
        """
        user = self.request.user
        
        if user.role == 'admin':
            # Admin can see all users
            return User.objects.all()
        elif user.role == 'faculty':
            # Faculty can see faculty, staff, and students (not admins)
            return User.objects.filter(role__in=['faculty', 'staff', 'student'])
        elif user.role == 'staff':
            # Staff can only see faculty
            return User.objects.filter(role='faculty')
        elif user.role == 'student':
            # Students can see faculty and other students
            return User.objects.filter(role__in=['faculty', 'student'])
        else:
            # Default: no access
            return User.objects.none()
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on HTTP method.
        
        Returns:
            Serializer class: UserCreateSerializer for POST, UserSerializer for GET
        """
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting individual users.
    
    GET: Retrieve user details
    PUT/PATCH: Update user information  
    DELETE: Delete user (admin only)
    
    Access Control:
    - Users can only access their own profile unless they're admin
    - Admins can access any user's profile
    - Update permissions are enforced at the serializer level
    
    Endpoints:
        GET /api/users/{id}/ - Get user details
        PUT /api/users/{id}/ - Update user (full update)
        PATCH /api/users/{id}/ - Update user (partial update)
        DELETE /api/users/{id}/ - Delete user (admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """
        Return the user object for the request.
        
        Users can only access their own profile unless they're admin or staff.
        
        Returns:
            User: User object based on permissions
        """
        # Users can only access their own profile unless they're admin
        if self.request.user.is_staff or self.request.user.role == 'admin':
            return super().get_object()
        return self.request.user
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on HTTP method.
        
        Returns:
            Serializer class: UserUpdateSerializer for PUT/PATCH, UserSerializer for GET
        """
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    User authentication endpoint.
    
    Authenticates user credentials and returns user data with authentication token.
    The token should be included in subsequent requests for authentication.
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "userpassword"
        }
    
    Response (Success):
        {
            "message": "Login successful",
            "user": {user_data},
            "token": "auth_token_string"
        }
    
    Response (Error):
        {
            "email": ["This field is required."],
            "password": ["This field is required."]
        }
    
    Args:
        request: HTTP request with login credentials
        
    Returns:
        Response: JSON response with user data and token or error messages
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        
        # Get or create token for user
        token, created = Token.objects.get_or_create(user=user)
        
        user_data = UserSerializer(user).data
        return Response({
            'message': 'Login successful',
            'user': user_data,
            'token': token.key
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint.
    
    Invalidates the user's authentication token and logs them out of the session.
    This ensures the token cannot be used for future requests.
    
    Args:
        request: HTTP request with authenticated user
        
    Returns:
        Response: JSON response confirming logout
    """
    try:
        # Delete the user's token to invalidate authentication
        request.user.auth_token.delete()
    except:
        # Handle case where token doesn't exist
        pass
    
    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """
    Get current user's profile information.
    
    Returns the authenticated user's profile data without sensitive information.
    This endpoint allows users to retrieve their own profile information.
    
    Args:
        request: HTTP request with authenticated user
        
    Returns:
        Response: JSON response with user profile data
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    """
    Change user password endpoint.
    
    Allows authenticated users to change their password by providing:
    - Current password for verification
    - New password meeting security requirements  
    - Confirmation of new password
    
    Request Body:
        {
            "old_password": "current_password",
            "new_password": "new_secure_password",
            "new_password_confirm": "new_secure_password"
        }
    
    Args:
        request: HTTP request with password change data
        
    Returns:
        Response: Success message or validation errors
    """
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_roles_view(request):
    """
    Get available user roles based on current user's permissions.
    
    Returns a list of roles that the current user is allowed to assign to others.
    The available roles depend on the user's own role and privileges:
    
    - Admin: Can assign all roles
    - Faculty: Can assign faculty, staff, and student roles
    - Staff: Can only assign faculty role
    - Student: Can assign faculty and student roles
    
    Args:
        request: HTTP request with authenticated user
        
    Returns:
        Response: JSON response with available roles array
    """
    from .models import UserRole
    current_user = request.user
    
    if current_user.role == 'admin':
        # Admin can see all roles
        roles = [{'value': choice[0], 'label': choice[1]} for choice in UserRole.choices]
    elif current_user.role == 'faculty':
        # Faculty can see faculty, staff, and students
        allowed_roles = ['faculty', 'staff', 'student']
        roles = [{'value': role, 'label': role.title()} for role in allowed_roles]
    elif current_user.role == 'staff':
        # Staff can only see faculty
        roles = [{'value': 'faculty', 'label': 'Faculty'}]
    elif current_user.role == 'student':
        # Students can see faculty and students
        allowed_roles = ['faculty', 'student']
        roles = [{'value': role, 'label': role.title()} for role in allowed_roles]
    else:
        roles = []
    
    return Response({'roles': roles})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def available_filter_roles(request):
    """
    Get available roles for filtering user lists.
    
    Returns role options that can be used to filter the user list display
    based on the current user's permissions. Includes an "All Roles" option
    for displaying unfiltered results.
    
    Args:
        request: HTTP request with authenticated user
        
    Returns:
        Response: JSON response with filter roles array
    """
    current_user = request.user
    
    base_roles = [{'value': '', 'label': 'All Roles'}]  # Empty value for all roles
    
    if current_user.role == 'admin':
        # Admin can filter by all roles
        filter_roles = [
            {'value': 'admin', 'label': 'Admins'},
            {'value': 'faculty', 'label': 'Faculty'},
            {'value': 'staff', 'label': 'Staff'},
            {'value': 'student', 'label': 'Students'}
        ]
    elif current_user.role == 'faculty':
        # Faculty can filter by faculty, staff, and students
        filter_roles = [
            {'value': 'faculty', 'label': 'Faculty'},
            {'value': 'staff', 'label': 'Staff'},
            {'value': 'student', 'label': 'Students'}
        ]
    elif current_user.role == 'staff':
        # Staff can only filter by faculty
        filter_roles = [
            {'value': 'faculty', 'label': 'Faculty'}
        ]
    elif current_user.role == 'student':
        # Students can filter by faculty and students
        filter_roles = [
            {'value': 'faculty', 'label': 'Faculty'},
            {'value': 'student', 'label': 'Students'}
        ]
    else:
        filter_roles = []
    
    return Response({'filter_roles': base_roles + filter_roles})


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def toggle_user_status(request, user_id):
    """
    Toggle user active status with role-based permissions.
    
    Allows authorized users to activate or deactivate other users based on
    their role permissions. Includes security checks to prevent users from
    modifying their own status or exceeding their permission level.
    
    Permission Rules:
    - Admin: Can toggle anyone's status
    - Faculty: Can only toggle students' status
    - Staff/Student: Cannot toggle anyone's status
    
    Args:
        request: HTTP request with authenticated user
        user_id: ID of the user whose status should be toggled
        
    Returns:
        Response: Success message with updated user data or error
    """
    current_user = request.user
    
    try:
        target_user = User.objects.get(id=user_id)
        
        # Prevent users from changing their own status
        if target_user.id == current_user.id:
            return Response({'error': 'Cannot change your own status'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Role-based permission checks
        if current_user.role == 'admin':
            # Admin can toggle anyone's status
            pass
        elif current_user.role == 'faculty':
            # Faculty can only toggle students
            if target_user.role != 'student':
                return Response({'error': 'Faculty can only deactivate students'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # Staff and students cannot toggle anyone's status
            return Response({'error': 'Insufficient permissions to change user status'}, status=status.HTTP_403_FORBIDDEN)
        
        target_user.is_active = not target_user.is_active
        target_user.save()
        
        action = "activated" if target_user.is_active else "deactivated"
        return Response({
            'message': f'User {target_user.username} has been {action}',
            'user': UserSerializer(target_user).data
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def change_user_role(request, user_id):
    """
    Change user role (admin only).
    
    Allows administrators to change another user's role. Includes validation
    to ensure the new role is valid and security checks to prevent admins
    from changing their own role.
    
    Request Body:
        {
            "role": "new_role_value"
        }
    
    Args:
        request: HTTP request with role change data
        user_id: ID of the user whose role should be changed
        
    Returns:
        Response: Success message with updated user data or error
    """
    if request.user.role != 'admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        new_role = request.data.get('role')
        
        if not new_role:
            return Response({'error': 'Role is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate role
        valid_roles = [choice[0] for choice in User._meta.get_field('role').choices]
        if new_role not in valid_roles:
            return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Prevent admin from changing their own role
        if user.id == request.user.id:
            return Response({'error': 'Cannot change your own role'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.role = new_role
        user.save()
        
        return Response({
            'message': f'User {user.username} role changed to {new_role}',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
