# Django User Management System

A comprehensive full-stack user management application featuring a Django REST API backend with role-based access control and a modern PyQt6 desktop frontend. This system provides secure user authentication, profile management, and administrative capabilities with an intuitive graphical interface.

## 🌟 Features

### Core Functionality
- **User Authentication**: Secure login/logout with email-based authentication
- **User Registration**: Self-service account creation with validation
- **Role-Based Access Control**: Four-tier permission system (Admin, Faculty, Staff, Student)
- **Profile Management**: Update personal information and change passwords
- **User Administration**: Comprehensive user management for authorized roles

### Security Features
- **Token-Based Authentication**: Stateless JWT-like token system
- **Password Security**: Django's built-in password hashing and validation
- **Input Validation**: Comprehensive server-side and client-side validation
- **Permission Control**: Granular access control based on user roles
- **Session Management**: Secure login/logout with token invalidation

### Technical Highlights
- **RESTful API**: Clean, well-documented REST endpoints
- **Modern GUI**: Responsive PyQt6 desktop interface
- **Error Handling**: Robust error handling with user-friendly messages
- **Logging**: Comprehensive logging for debugging and monitoring
- **Database Management**: SQLite for development, easily configurable for production

## 🏗️ Architecture

```
┌─────────────────────┐    HTTP/JSON API    ┌─────────────────────┐
│   PyQt6 Frontend    │ ◄─────────────────► │   Django Backend    │
│                     │                     │                     │
│ ┌─────────────────┐ │                     │ ┌─────────────────┐ │
│ │ Login/Register  │ │                     │ │ Authentication  │ │
│ │ User Dashboard  │ │                     │ │ User Management │ │
│ │ Admin Panel     │ │                     │ │ Role Control    │ │
│ └─────────────────┘ │                     │ └─────────────────┘ │
│                     │                     │                     │
│ ┌─────────────────┐ │                     │ ┌─────────────────┐ │
│ │ API Services    │ │                     │ │ REST API        │ │
│ │ Data Models     │ │                     │ │ Database ORM    │ │
│ │ UI Components   │ │                     │ │ Admin Interface │ │
│ └─────────────────┘ │                     │ └─────────────────┘ │
└─────────────────────┘                     └─────────────────────┘
                                                       │
                                            ┌─────────────────────┐
                                            │   SQLite Database   │
                                            │                     │
                                            │ • User Accounts     │
                                            │ • Authentication    │
                                            │ • Role Management   │
                                            │ • Audit Trails      │
                                            └─────────────────────┘
```

## 📊 Role-Based Permissions

| Feature | Admin | Faculty | Staff | Student |
|---------|-------|---------|-------|---------|
| View All Users | ✅ | ✅* | ✅* | ✅* |
| Create Users | ✅ | ✅ | ❌ | ❌ |
| Edit Own Profile | ✅ | ✅ | ✅ | ✅ |
| Edit Other Users | ✅ | ✅** | ❌ | ❌ |
| Delete Users | ✅ | ❌ | ❌ | ❌ |
| Change User Roles | ✅ | ❌ | ❌ | ❌ |
| Activate/Deactivate | ✅ | ✅** | ❌ | ❌ |
| System Administration | ✅ | ❌ | ❌ | ❌ |

*Limited to users within their permission scope  
**Limited to students only

## 🗂️ Project Structure

```
Django User/
├── 📁 backend/                     # Django REST API
│   ├── 📁 apps/
│   │   └── 📁 Users/              # User management app
│   │       ├── 📄 models.py       # User model & role definitions
│   │       ├── 📄 views.py        # API endpoints & business logic
│   │       ├── 📄 serializers.py  # Data validation & serialization
│   │       ├── 📄 urls.py         # URL routing configuration
│   │       ├── 📄 admin.py        # Django admin interface
│   │       └── 📁 migrations/     # Database schema changes
│   ├── 📁 config/                 # Django project settings
│   │   ├── 📄 settings.py         # Application configuration
│   │   ├── 📄 urls.py            # Root URL configuration
│   │   └── 📄 wsgi.py            # WSGI deployment interface
│   └── 📄 manage.py               # Django management commands
├── 📁 frontend/                   # PyQt6 Desktop Application
│   ├── 📄 main.py                 # Application entry point
│   ├── 📁 models/                 # Data models
│   │   └── 📄 user.py            # Frontend user model
│   ├── 📁 services/               # API communication layer
│   │   └── 📄 services.py        # HTTP client & API wrapper
│   ├── 📁 ui/                     # User interface components
│   │   ├── 📄 login_window.py    # Authentication interface
│   │   ├── 📄 register_window.py # User registration form
│   │   └── 📄 dashboard.py       # Main application dashboard
│   └── 📁 utils/                  # Utility functions
│       └── 📄 validators.py      # Input validation helpers
├── 📁 testing/                    # Development & testing utilities
│   ├── 📄 test_connection.py     # Backend connectivity test
│   ├── 📄 populate.py            # Sample data generator
│   ├── 📄 preview_db.py          # Database inspection tool
│   └── 📄 wipe_all.py            # Data cleanup utility
├── 📄 requirements.txt            # Python dependencies
├── 📄 setup.bat / setup.sh        # Automated setup scripts
├── 📄 start_app.bat / start_app.sh # Application launcher scripts
├── 📄 API_DOCUMENTATION.md        # Complete API reference
├── 📄 DEVELOPER_GUIDE.md          # Developer documentation
├── 📄 IMPROVEMENTS.md             # Enhancement suggestions
└── 📄 README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (Required for PyQt6 compatibility)
- **Git** (For version control)
- **Virtual Environment** (Recommended for dependency isolation)

### Automated Setup (Recommended)

#### Windows
```cmd
# Clone the repository
git clone <repository-url>
cd "Django User"

# Run automated setup
setup.bat

# Start the application
start_app.bat
```

#### Linux/macOS
```bash
# Clone the repository
git clone <repository-url>
cd "Django User"

# Make scripts executable
chmod +x setup.sh start_app.sh

# Run automated setup
./setup.sh

# Start the application
./start_app.sh
```

### Manual Setup

1. **Environment Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Database Configuration**
   ```bash
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. **Verification**
   ```bash
   # Test backend connectivity
   python testing/test_connection.py
   
   # Populate sample data (optional)
   python testing/populate.py
   ```

## 🖥️ Usage Guide

### Starting the Application

1. **Start Django Backend**
   ```bash
   cd backend
   python manage.py runserver
   ```
   Server will run at: `http://127.0.0.1:8000`

2. **Launch Frontend Application**
   ```bash
   cd frontend
   python main.py
   ```

### Default Admin Account
After running `createsuperuser`, you can also create a default admin via the Django admin panel:
- URL: `http://127.0.0.1:8000/admin/`
- Use your superuser credentials

### Application Workflow

1. **Login/Registration**
   - New users can register with email and password
   - Existing users log in with email/password
   - Default role for new users: Student

2. **Dashboard Features**
   - View user profile information
   - Change password securely
   - Role-based user management (if authorized)
   - User status management (if authorized)

3. **Administrative Functions**
   - User role assignment (Admin only)
   - Account activation/deactivation
   - User creation and management

## 🛠️ Development

### API Endpoints
See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete endpoint reference.

### Development Environment
Detailed setup and development guidelines available in [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md).

### Testing
```bash
# Backend connectivity test
python testing/test_connection.py

# Django unit tests
cd backend
python manage.py test

# Frontend integration test
cd frontend
python main.py
```

## 🔧 Configuration

### Environment Variables
Create `.env` file in backend directory:
```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
API_BASE_URL=http://127.0.0.1:8000/api
LOG_LEVEL=INFO
```

### Database Configuration
- **Development**: SQLite (included)
- **Production**: PostgreSQL/MySQL (requires configuration)

## 📚 Documentation

- **[API Documentation](API_DOCUMENTATION.md)**: Complete REST API reference
- **[Developer Guide](DEVELOPER_GUIDE.md)**: Architecture, patterns, and development workflow
- **[Improvements](IMPROVEMENTS.md)**: Planned enhancements and feature requests

## 🧪 Testing Utilities

### Backend Testing
```bash
# Connectivity test
python testing/test_connection.py

# Sample data population
python testing/populate.py

# Database inspection
python testing/preview_db.py

# Clean database
python testing/wipe_all.py
```

## 🚀 Deployment

### Development Deployment
Use the provided startup scripts for local development.

### Production Deployment
1. Configure production database (PostgreSQL recommended)
2. Set environment variables for production
3. Use WSGI server (Gunicorn + Nginx recommended)
4. Enable HTTPS and security headers
5. Configure logging and monitoring

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for detailed deployment instructions.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for coding standards and development workflow.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Ensure Django server is running on port 8000
   - Check firewall settings
   - Run `python testing/test_connection.py`

2. **Login Issues**
   - Verify user account exists and is active
   - Check email/password combination
   - Ensure backend database is properly migrated

3. **Permission Errors**
   - Verify user role and permissions
   - Check role-based access control settings
   - Confirm API endpoint accessibility

### Getting Help
- Check the documentation files for detailed information
- Review error logs in the terminal output
- Use the testing utilities to diagnose issues
- Create an issue in the repository for bugs or feature requests

## 🔄 Recent Updates

- Enhanced documentation with comprehensive guides
- Improved error handling and user feedback
- Added role-based permission system
- Implemented secure authentication flow
- Added comprehensive testing utilities
- Created automated setup and deployment scripts

---

**Built with ❤️ using Django, Django REST Framework, and PyQt6**
cd "Django User"
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

Copy the environment configuration files:

**Backend:**
```bash
copy backend\.env.example backend\.env
```

**Frontend:**
```bash
copy frontend\.env frontend\.env
```

Edit `backend\.env` if needed:
- `DJANGO_SECRET_KEY`: Generate a new secret key for production
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Add your domain for production

### 6. Set Up Database

Navigate to the backend directory and run migrations:

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser  # Optional: Create admin user
cd ..
```

### 7. Run the Application

**Option A: Use the startup script (Windows only):**
```bash
start_app.bat
```

**Option B: Manual startup:**

1. Start the Django backend (in one terminal):
```bash
cd backend
python manage.py runserver
```

2. Start the PyQt6 frontend (in another terminal):
```bash
python frontend/main.py
```

## Development

### Backend Development

The Django backend provides a REST API with the following endpoints:

- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login
- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/profile/` - Update user profile

### Frontend Development

The PyQt6 frontend includes:

- Login window (`frontend/ui/login_window.py`)
- Registration window (`frontend/ui/register_window.py`)
- Dashboard (`frontend/ui/dashboard.py`)
- API service layer (`frontend/services/services.py`)

### Running Tests

```bash
# Test backend connection
python testing/test_connection.py

# Run Django tests
cd backend
python manage.py test

# Run frontend tests
python frontend/test_roles.py
```

### Useful Scripts

- `testing/populate.py` - Populate database with sample data
- `testing/preview_db.py` - Preview database contents
- `testing/wipe_all.py` - Clear all data
- `testing/test_connection.py` - Test backend connectivity

## Database Schema

### User Model
- `id` - Primary key
- `username` - Username
- `email` - Email (unique, used for login)
- `password` - Hashed password
- `role` - User role (admin/student/faculty/staff)
- `is_active` - Account status
- `created_at` - Registration timestamp
- `updated_at` - Last update timestamp

## API Documentation

### Authentication

The API uses token-based authentication. Include the token in the Authorization header:

```
Authorization: Token your-token-here
```

### User Registration

```http
POST /api/users/register/
Content-Type: application/json

{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "secure_password",
    "role": "student"
}
```

### User Login

```http
POST /api/users/login/
Content-Type: application/json

{
    "email": "john@example.com",
    "password": "secure_password"
}
```

## Troubleshooting

### Common Issues

1. **"Virtual environment not found"**
   - Make sure you created the virtual environment: `python -m venv venv`

2. **"Django backend is not running"**
   - Check if port 8000 is available
   - Ensure migrations are applied: `python manage.py migrate`

3. **"Module not found" errors**
   - Activate virtual environment: `venv\Scripts\activate`
   - Install dependencies: `pip install -r requirements.txt`

4. **Database issues**
   - Delete `backend/db.sqlite3` and run `python manage.py migrate` again

### Environment Variables

Make sure these environment files exist and are properly configured:

- `backend/.env` - Django configuration
- `frontend/.env` - Frontend configuration

### Dependencies

If you encounter dependency issues, try:

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test your changes
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Create a Pull Request

## License

This project is licensed under the MIT License.
