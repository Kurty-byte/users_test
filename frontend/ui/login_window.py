from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal

class LoginWindow(QWidget):
    login_success = pyqtSignal(object)  # Signal to emit when login is successful
    switch_to_register = pyqtSignal()   # Signal to switch to register window
    
    def __init__(self, user_service):
        super().__init__()
        self.user_service = user_service
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Login')
        self.setFixedSize(350, 250)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel('Login to Your Account')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 20px;
                color: #2c3e50;
            }
        """)
        
        # Input fields
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('Email')
        self.email_input.setStyleSheet("padding: 8px; font-size: 12px;")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("padding: 8px; font-size: 12px;")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton('Login')
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-size: 12px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.register_button = QPushButton('Register')
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px;
                font-size: 12px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        # Connect signals
        self.login_button.clicked.connect(self.handle_login)
        self.register_button.clicked.connect(self.switch_to_register.emit)
        self.password_input.returnPressed.connect(self.handle_login)
        
        # Layout
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        
        layout.addWidget(title_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def handle_login(self):
        """Handle login attempt with improved error handling"""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        # Validate inputs
        if not email or not password:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields")
            return
        
        # Basic email validation
        if '@' not in email or '.' not in email.split('@')[-1]:
            QMessageBox.warning(self, "Input Error", "Please enter a valid email address")
            return
        
        # Disable login button to prevent multiple clicks
        self.login_button.setEnabled(False)
        self.login_button.setText("Logging in...")
        
        try:
            result = self.user_service.login(email, password)
            
            if result['success']:
                self.login_success.emit(result['user'])
                self.close()
            else:
                # Handle different error types
                error_msg = result.get('error', 'Login failed')
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get('detail', 'Login failed')
                
                # Provide user-friendly error messages
                if 'Invalid credentials' in str(error_msg).lower():
                    error_msg = "Invalid email or password. Please check your credentials and try again."
                elif 'connection' in str(error_msg).lower():
                    error_msg = "Unable to connect to server. Please check your internet connection and try again."
                elif 'timeout' in str(error_msg).lower():
                    error_msg = "Request timed out. The server may be experiencing high load. Please try again."
                
                QMessageBox.critical(self, "Login Failed", str(error_msg))
                
        except Exception as e:
            error_message = (
                "An unexpected error occurred while trying to log in.\n\n"
                "Please ensure:\n"
                "• The Django backend server is running\n"
                "• Your internet connection is stable\n"
                "• The server address is correct\n\n"
                f"Technical details: {str(e)}"
            )
            QMessageBox.critical(self, "Connection Error", error_message)
        
        finally:
            # Re-enable login button
            self.login_button.setEnabled(True)
            self.login_button.setText("Login")
    
    def clear_inputs(self):
        self.email_input.clear()
        self.password_input.clear()
