from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from models.user import UserRole
import re

class RegisterWindow(QWidget):
    registration_success = pyqtSignal()  # Signal to emit when registration is successful
    switch_to_login = pyqtSignal()       # Signal to switch to login window
    
    def __init__(self, user_service):
        super().__init__()
        self.user_service = user_service
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Register')
        self.setFixedSize(350, 380)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel('Create New Account')
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
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        self.username_input.setStyleSheet("padding: 8px; font-size: 12px;")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('Email')
        self.email_input.setStyleSheet("padding: 8px; font-size: 12px;")
        
        # Role selection
        role_label = QLabel('Select Role:')
        role_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        self.role_combo = QComboBox()
        self.role_combo.addItem("Student", UserRole.STUDENT)
        self.role_combo.addItem("Faculty", UserRole.FACULTY)
        self.role_combo.addItem("Staff", UserRole.STAFF)
        self.role_combo.addItem("Admin", UserRole.ADMIN)
        self.role_combo.setStyleSheet("padding: 8px; font-size: 12px;")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("padding: 8px; font-size: 12px;")
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText('Confirm Password')
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setStyleSheet("padding: 8px; font-size: 12px;")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.register_button = QPushButton('Register')
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                font-size: 12px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        self.back_button = QPushButton('Back to Login')
        self.back_button.setStyleSheet("""
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
        self.register_button.clicked.connect(self.handle_register)
        self.back_button.clicked.connect(self.switch_to_login.emit)
        
        # Layout
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.back_button)
        
        layout.addWidget(title_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.email_input)
        layout.addWidget(role_label)
        layout.addWidget(self.role_combo)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_password_input)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def handle_register(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        selected_role = self.role_combo.currentData()
        
        # Validation
        if not all([username, email, password, confirm_password]):
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
            return
        
        if not self.is_valid_email(email):
            QMessageBox.warning(self, "Error", "Please enter a valid email address")
            return
        
        # Use the Django API register method
        result = self.user_service.register(username, email, password, confirm_password, selected_role)
        
        if result['success']:
            QMessageBox.information(self, "Success", result['message'])
            self.registration_success.emit()
            self.clear_inputs()
        else:
            error_msg = result['error']
            if isinstance(error_msg, dict):
                # Extract specific field errors
                error_details = []
                for field, errors in error_msg.items():
                    if isinstance(errors, list):
                        error_details.extend(errors)
                    else:
                        error_details.append(str(errors))
                error_message = '\n'.join(error_details)
            else:
                error_message = str(error_msg)
            QMessageBox.critical(self, "Registration Failed", error_message)
    
    def is_valid_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def clear_inputs(self):
        self.username_input.clear()
        self.email_input.clear()
        self.role_combo.setCurrentIndex(0)  # Reset to first option (Student)
        self.password_input.clear()
        self.confirm_password_input.clear()
