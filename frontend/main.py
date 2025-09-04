import sys
from PyQt6.QtWidgets import QApplication
from services.services import UserService
from ui.login_window import LoginWindow
from ui.register_window import RegisterWindow
from ui.dashboard import Dashboard

class UserApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.user_service = UserService()
        self.current_user = None
        
        # Initialize windows
        self.login_window = LoginWindow(self.user_service)
        self.register_window = RegisterWindow(self.user_service)
        self.dashboard = None
        
        # Connect signals
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.switch_to_register.connect(self.show_register)
        
        self.register_window.registration_success.connect(self.show_login)
        self.register_window.switch_to_login.connect(self.show_login)
    
    def run(self):
        self.show_login()
        return self.app.exec()
    
    def show_login(self):
        self.register_window.hide()
        if self.dashboard:
            self.dashboard.hide()
        self.login_window.clear_inputs()
        self.login_window.show()
    
    def show_register(self):
        self.login_window.hide()
        self.register_window.clear_inputs()
        self.register_window.show()
    
    def on_login_success(self, user):
        self.current_user = user
        self.login_window.hide()
        
        # Create dashboard
        self.dashboard = Dashboard(self.user_service, self.current_user)
        self.dashboard.logout_requested.connect(self.on_logout)
        self.dashboard.show()
    
    def on_logout(self):
        # Call Django logout API
        result = self.user_service.logout()
        
        self.current_user = None
        if self.dashboard:
            self.dashboard.hide()
        self.show_login()

def main():
    app = UserApp()
    sys.exit(app.run())

if __name__ == '__main__':
    main()