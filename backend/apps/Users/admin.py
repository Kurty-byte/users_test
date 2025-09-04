"""
Django Admin Configuration for User Management

This module configures the Django admin interface for the custom User model,
providing a comprehensive admin panel for user management with enhanced
functionality beyond the default Django admin.

Features:
- Enhanced user listing with role and activity status
- Advanced filtering by role, status, and creation date
- Search capabilities across username and email
- Custom fieldsets for better organization
- Read-only timestamp fields
- Optimized add user form with required fields

The admin interface is designed for system administrators to efficiently
manage users, view system statistics, and perform bulk operations.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Enhanced Django admin configuration for User model.
    
    This admin class extends Django's built-in UserAdmin to provide
    better integration with our custom User model and role-based system.
    
    Features:
        - Custom list display with role and timestamp information
        - Advanced filtering options for better user management
        - Search functionality across key user fields
        - Organized fieldsets for clean form presentation
        - Read-only fields for audit trail preservation
        - Enhanced add user form with custom fields
    """
    
    # List view configuration
    list_display = [
        'username', 
        'email', 
        'role', 
        'is_active', 
        'is_staff', 
        'created_at',
        'last_login'
    ]
    
    list_filter = [
        'role', 
        'is_active', 
        'is_staff', 
        'is_superuser',
        'created_at',
        'last_login'
    ]
    
    search_fields = [
        'username', 
        'email', 
        'first_name', 
        'last_name'
    ]
    
    ordering = ['-created_at']  # Show newest users first
    
    # Detail view configuration
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Status', {
            'fields': ('role',),
            'description': 'User role determines access permissions and available features.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Automatic timestamp tracking for audit purposes.'
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    
    # Add user form configuration
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('User Information', {
            'fields': ('email', 'first_name', 'last_name'),
            'description': 'Basic user information and contact details.'
        }),
        ('Role Assignment', {
            'fields': ('role',),
            'description': 'Assign appropriate role based on user responsibilities.'
        }),
    )
    
    # Performance optimizations
    list_per_page = 25
    list_max_show_all = 100
    
    def get_queryset(self, request):
        """
        Optimize queryset for admin list view.
        
        Args:
            request: HTTP request object
            
        Returns:
            QuerySet: Optimized user queryset
        """
        return super().get_queryset(request).select_related()
    
    def has_delete_permission(self, request, obj=None):
        """
        Control delete permissions in admin.
        
        Prevents deletion of superusers and the current user to maintain
        system integrity and prevent accidental lockouts.
        
        Args:
            request: HTTP request object
            obj: User object being deleted (if any)
            
        Returns:
            bool: Whether deletion is permitted
        """
        if obj and obj.is_superuser:
            return False  # Don't allow deletion of superusers
        if obj and obj == request.user:
            return False  # Don't allow users to delete themselves
        return super().has_delete_permission(request, obj)
    
    def save_model(self, request, obj, form, change):
        """
        Custom save behavior for admin form.
        
        Ensures proper handling of user creation and updates,
        including email normalization and password handling.
        
        Args:
            request: HTTP request object
            obj: User object being saved
            form: Admin form instance
            change: Whether this is an update (True) or creation (False)
        """
        if not change:
            # For new users, ensure email is normalized
            obj.email = obj.email.lower().strip()
        
        super().save_model(request, obj, form, change)
    
    # Custom admin actions
    actions = ['activate_users', 'deactivate_users', 'reset_passwords']
    
    def activate_users(self, request, queryset):
        """
        Admin action to activate selected users.
        
        Args:
            request: HTTP request object
            queryset: Selected user queryset
        """
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users have been activated.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """
        Admin action to deactivate selected users.
        
        Args:
            request: HTTP request object
            queryset: Selected user queryset
        """
        # Prevent deactivating superusers and current user
        safe_queryset = queryset.exclude(is_superuser=True).exclude(id=request.user.id)
        updated = safe_queryset.update(is_active=False)
        self.message_user(request, f'{updated} users have been deactivated.')
    deactivate_users.short_description = "Deactivate selected users"
