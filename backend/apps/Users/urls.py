from django.urls import path
from . import views

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
    
    # Utility endpoints
    path('roles/', views.user_roles_view, name='user_roles'),
    path('filter-roles/', views.available_filter_roles, name='filter_roles'),
]
