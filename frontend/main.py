"""
PyQt6 User Management Frontend Application

This module serves as the main entry point for the PyQt6 desktop application
that interfaces with the Django User Management API. It orchestrates the
application flow between login, registration, and dashboard windows.

The application implements a token-based authentication system and provides
a desktop GUI for user management operations with role-based access control.

Classes:
    UserApp: Main application controller managing window transitions and user state

Functions:
    main: Application entry point and startup function
"""

import sys
from PyQt6.QtWidgets import QApplication
from services.services import UserService
from ui.login_window import LoginWindow
from ui.register_window import RegisterWindow
from ui.dashboard import Dashboard


class UserApp:
    """
    Main application controller for the User Management frontend.
    
    This class manages the overall application state, coordinates between
    different UI windows, and handles user authentication flow. It serves
    as the central coordinator for all user interface components.
    
    Attributes:
        app (QApplication): PyQt6 application instance
        user_service (UserService): Service for API communication
        current_user (User): Currently authenticated user object
        login_window (LoginWindow): User login interface
        register_window (RegisterWindow): User registration interface
        dashboard (Dashboard): Main application dashboard (created after login)
    
    The application flow:
    1. Start with login window
    2. Allow switching to registration
    3. After successful login, show dashboard
    4. Handle logout and return to login
    """
    
    def __init__(self):
        """
        Initialize the PyQt6 application and set up UI components.
        
        Creates the main application instance, initializes the API service,
        sets up all UI windows, and connects signal handlers for window transitions.
        """
        self.app = QApplication(sys.argv)
        self.user_service = UserService()
        self.current_user = None
        
        # Initialize windows
        self.login_window = LoginWindow(self.user_service)
        self.register_window = RegisterWindow(self.user_service)
        self.dashboard = None
        
        # Connect signals for window navigation
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.switch_to_register.connect(self.show_register)
        
        self.register_window.registration_success.connect(self.show_login)
        self.register_window.switch_to_login.connect(self.show_login)
    
    def run(self):
        """
        Start the application and show the initial login window.
        
        Returns:
            int: Application exit code from PyQt6 event loop
        """
        self.show_login()
        return self.app.exec()
    
    def show_login(self):
        """
        Display the login window and hide other windows.
        
        This method is called when:
        - Application starts
        - User clicks "Back to Login" from registration
        - User logs out from dashboard
        """
        self.register_window.hide()
        if self.dashboard:
            self.dashboard.hide()
        self.login_window.clear_inputs()
        self.login_window.show()
    
    def show_register(self):
        """
        Display the registration window and hide the login window.
        
        Called when user clicks "Register" from the login window.
        """
        self.login_window.hide()
        self.register_window.clear_inputs()
        self.register_window.show()
    
    def on_login_success(self, user):
        """
        Handle successful user login.
        
        Called when the login window emits the login_success signal.
        This method transitions the user to the main application dashboard.
        
        Args:
            user (User): The authenticated user object
        """
        self.current_user = user
        self.login_window.hide()
        
        # Create and show dashboard
        self.dashboard = Dashboard(self.user_service, self.current_user)
        self.dashboard.logout_requested.connect(self.on_logout)
        self.dashboard.show()
    
    def on_logout(self):
        """
        Handle user logout request.
        
        Called when the dashboard emits the logout_requested signal.
        This method calls the API logout endpoint and returns to login window.
        """
        # Call Django logout API to invalidate token
        result = self.user_service.logout()
        
        # Clear current user and return to login
        self.current_user = None
        if self.dashboard:
            self.dashboard.hide()
        self.show_login()


def main():
    """
    Application entry point.
    
    Creates and runs the main UserApp instance. This function handles
    the application startup and ensures proper exit code handling.
    
    Returns:
        None: Function exits the Python interpreter with the application exit code
    """
    app = UserApp()
    sys.exit(app.run())


if __name__ == '__main__':
    main()