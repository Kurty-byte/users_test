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
    Custom permission to only allow admins to view user list,
    but allow anyone to create users (registration).
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True  # Allow registration
        # For GET requests, check if user is authenticated
        return request.user.is_authenticated


class UserListCreateView(generics.ListCreateAPIView):
    """
    GET: List users based on role permissions
    POST: Create a new user (public registration)
    """
    permission_classes = [IsAdminOrCreateOnly]
    
    def get_queryset(self):
        """Filter users based on current user's role"""
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
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve user details
    PUT/PATCH: Update user information
    DELETE: Delete user (admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        # Users can only access their own profile unless they're admin
        if self.request.user.is_staff or self.request.user.role == 'admin':
            return super().get_object()
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """User login endpoint"""
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
    """User logout endpoint"""
    try:
        # Delete the user's token
        request.user.auth_token.delete()
    except:
        pass
    
    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """Get current user's profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    """Change user password"""
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_roles_view(request):
    """Get available user roles based on current user's permissions"""
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
    """Get available roles for filtering based on current user's permissions"""
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
    """Toggle user active status with role-based permissions"""
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
    """Change user role (admin only)"""
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
