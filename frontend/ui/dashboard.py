from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, 
                             QHeaderView, QAbstractItemView, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal
from models.user import UserRole

class Dashboard(QWidget):
    logout_requested = pyqtSignal()
    
    def __init__(self, user_service, current_user):
        super().__init__()
        self.user_service = user_service
        self.current_user = current_user
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f'User Dashboard - {self.current_user.role.value.title()}')
        self.setGeometry(300, 300, 800, 500)
        
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        welcome_label = QLabel(f'Welcome, {self.current_user.username}! ({self.current_user.role.value.title()})')
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)
        
        logout_button = QPushButton('Logout')
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 16px;
                font-size: 12px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_button.clicked.connect(self.logout_requested.emit)
        
        header_layout.addWidget(welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(logout_button)
        
        # User info
        info_label = QLabel('User Information')
        info_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        
        user_details = QLabel(f"""Username: {self.current_user.username}
Email: {self.current_user.email}
Role: {self.current_user.role.value.title()}
Status: {'Active' if self.current_user.is_active else 'Inactive'}""")
        user_details.setStyleSheet("padding: 10px; background-color: #808080; border-radius: 5px;")
        
        # Role filter for users table
        filter_layout = QHBoxLayout()
        filter_label = QLabel('Filter by Role:')
        filter_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        self.role_filter = QComboBox()
        self.load_filter_roles()  # Load roles based on user permissions
        self.role_filter.currentIndexChanged.connect(self.load_users_table)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.role_filter)
        filter_layout.addStretch()
        
        # Users table
        table_label = QLabel('All Users')
        table_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        
        self.users_table = QTableWidget()
        self.setup_users_table()
        self.load_users_table()
        
        # Admin controls (show based on user role permissions)
        if self.should_show_admin_controls():
            admin_controls_layout = QHBoxLayout()
            
            # Only show toggle status for admin and faculty
            if self.current_user.role in [UserRole.ADMIN, UserRole.FACULTY]:
                self.toggle_status_button = QPushButton('Toggle Status')
                self.toggle_status_button.clicked.connect(self.toggle_selected_user_status)
            
            # Only show change role for admin
            if self.current_user.role == UserRole.ADMIN:
                self.change_role_button = QPushButton('Change Role')
                self.change_role_button.clicked.connect(self.change_selected_user_role)
            
            # Style admin buttons
            button_style = """
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 8px 12px;
                    font-size: 10px;
                    border: none;
                    border-radius: 3px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """
            
            admin_controls_layout.addWidget(QLabel("Admin Controls:"))
            
            if hasattr(self, 'toggle_status_button'):
                self.toggle_status_button.setStyleSheet(button_style)
                admin_controls_layout.addWidget(self.toggle_status_button)
            
            if hasattr(self, 'change_role_button'):
                self.change_role_button.setStyleSheet(button_style)
                admin_controls_layout.addWidget(self.change_role_button)
            
            admin_controls_layout.addStretch()
        
        # Layout
        layout.addLayout(header_layout)
        layout.addWidget(info_label)
        layout.addWidget(user_details)
        layout.addLayout(filter_layout)
        layout.addWidget(table_label)
        layout.addWidget(self.users_table)
        if self.should_show_admin_controls():
            layout.addLayout(admin_controls_layout)
        
        self.setLayout(layout)
    
    def should_show_admin_controls(self):
        """Determine if admin controls should be shown based on user role"""
        return self.current_user.role in [UserRole.ADMIN, UserRole.FACULTY]
    
    def load_filter_roles(self):
        """Load available filter roles based on user permissions"""
        result = self.user_service.get_available_filter_roles()
        if result.get('success'):
            self.role_filter.clear()
            for role_info in result['filter_roles']:
                self.role_filter.addItem(role_info['label'], role_info['value'])
        else:
            # Fallback to basic roles if API fails
            self.role_filter.addItem("All Roles", "")
    
    def setup_users_table(self):
        """Setup the users table with proper headers and styling"""
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(['ID', 'Username', 'Email', 'Role', 'Status'])
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.users_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # Make table columns resize properly
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    
    def load_users_table(self):
        """Load users into the table based on role filter"""
        selected_role = self.role_filter.currentData()
        
        # Get all users (already filtered by backend based on user role)
        result = self.user_service.get_all_users()
        if not result.get('success'):
            users = []
        else:
            all_users = result.get('users', [])
            # Apply frontend filter if a specific role is selected
            if selected_role:
                users = [user for user in all_users if user.role.value == selected_role]
            else:
                users = all_users
        
        self.users_table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.users_table.setItem(row, 1, QTableWidgetItem(user.username))
            self.users_table.setItem(row, 2, QTableWidgetItem(user.email))
            self.users_table.setItem(row, 3, QTableWidgetItem(user.role.value.title()))
            
            # Enhanced status display
            status_text = 'Active' if user.is_active else 'Inactive'
            if user.id == self.current_user.id:
                status_text += ' (You)'
            
            status_item = QTableWidgetItem(status_text)
            if user.is_active:
                status_item.setBackground(Qt.GlobalColor.lightGray)
            else:
                status_item.setBackground(Qt.GlobalColor.yellow)
            self.users_table.setItem(row, 4, status_item)
    
    def get_selected_user_id(self):
        """Get the ID of the currently selected user"""
        current_row = self.users_table.currentRow()
        if current_row >= 0:
            id_item = self.users_table.item(current_row, 0)
            if id_item:
                return int(id_item.text())
        return None
    
    def toggle_selected_user_status(self):
        """Toggle the active status of the selected user"""
        user_id = self.get_selected_user_id()
        if user_id is None:
            QMessageBox.warning(self, "Warning", "Please select a user first")
            return
        
        # Check if trying to modify own account
        if user_id == self.current_user.id:
            QMessageBox.warning(self, "Warning", "You cannot change your own status")
            return
        
        # Additional check for faculty role
        if self.current_user.role == UserRole.FACULTY:
            # Get selected user's role from table
            current_row = self.users_table.currentRow()
            if current_row >= 0:
                role_item = self.users_table.item(current_row, 3)
                if role_item and role_item.text().lower() != 'student':
                    QMessageBox.warning(self, "Warning", "Faculty can only toggle student status")
                    return
        
        result = self.user_service.toggle_user_status(user_id)
        if result['success']:
            QMessageBox.information(self, "Success", result['message'])
            self.load_users_table()
        else:
            QMessageBox.critical(self, "Error", result['error'])
    
    def change_selected_user_role(self):
        """Change the role of the selected user"""
        user_id = self.get_selected_user_id()
        if user_id is None:
            QMessageBox.warning(self, "Warning", "Please select a user first")
            return
        
        # Check if trying to modify own account
        if user_id == self.current_user.id:
            QMessageBox.warning(self, "Warning", "You cannot change your own role")
            return
        
        # Create a dialog to select new role
        dialog = QDialog(self)
        dialog.setWindowTitle("Change User Role")
        dialog.setFixedSize(300, 150)
        
        layout = QVBoxLayout()
        
        role_label = QLabel("Select new role:")
        role_combo = QComboBox()
        role_combo.addItem("Student", UserRole.STUDENT)
        role_combo.addItem("Faculty", UserRole.FACULTY)
        role_combo.addItem("Staff", UserRole.STAFF)
        role_combo.addItem("Admin", UserRole.ADMIN)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        layout.addWidget(role_label)
        layout.addWidget(role_combo)
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_role = role_combo.currentData()
            result = self.user_service.change_user_role(user_id, new_role.value)
            if result['success']:
                QMessageBox.information(self, "Success", result['message'])
                self.load_users_table()
            else:
                QMessageBox.critical(self, "Error", result['error'])
