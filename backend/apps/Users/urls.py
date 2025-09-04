"""
Django URL Configuration for User Management API

This module defines all the URL patterns for the User Management API endpoints.
It maps URL paths to their corresponding view functions and classes, providing
a RESTful API interface for user authentication and management operations.

URL Patterns:
    Authentication:
        - POST /auth/login/ - User login
        - POST /auth/logout/ - User logout  
        - GET /auth/profile/ - Get current user profile
        - POST /auth/change-password/ - Change password

    User Management:
        - GET /users/ - List users (filtered by role)
        - POST /users/ - Create new user (registration)
        - GET /users/{id}/ - Get user details
        - PUT/PATCH /users/{id}/ - Update user
        - DELETE /users/{id}/ - Delete user
        - PATCH /users/{id}/toggle-status/ - Toggle user active status
        - PATCH /users/{id}/change-role/ - Change user role

    Utility:
        - GET /roles/ - Get available roles for current user
        - GET /filter-roles/ - Get roles for filtering user lists

All endpoints implement appropriate permissions and role-based access control.
"""

from django.urls import path
from . import views

# App namespace for URL reversing
app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/profile/', views.profile_view, name='profile'),
    path('auth/change-password/', views.change_password_view, name='change_password'),
    
    # User management endpoints
    path('users/', views.UserListCreateView.as_view(), name='user_list_create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/change-role/', views.change_user_role, name='change_user_role'),
    
    # Utility endpoints for role management
    path('roles/', views.user_roles_view, name='user_roles'),
    path('filter-roles/', views.available_filter_roles, name='filter_roles'),
]
