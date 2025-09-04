# Django User Management System - Developer Documentation

## Overview

This comprehensive guide provides detailed information for developers working with the Django User Management System. It covers architecture, development workflows, testing procedures, and deployment considerations.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Code Structure](#code-structure)
4. [Development Workflow](#development-workflow)
5. [Testing Guide](#testing-guide)
6. [API Design Patterns](#api-design-patterns)
7. [Frontend Architecture](#frontend-architecture)
8. [Security Implementation](#security-implementation)
9. [Performance Considerations](#performance-considerations)
10. [Deployment Guide](#deployment-guide)
11. [Troubleshooting](#troubleshooting)

## Architecture Overview

### System Components

```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│   PyQt6 GUI     │ ◄─────────────► │  Django REST    │
│   Frontend      │                 │     API         │
└─────────────────┘                 └─────────────────┘
         │                                    │
         │                                    │
    ┌─────────┐                          ┌─────────┐
    │ Models  │                          │ Models  │
    │ Services│                          │ Views   │
    │ UI      │                          │ Serializ│
    └─────────┘                          └─────────┘
                                              │
                                         ┌─────────┐
                                         │ SQLite  │
                                         │Database │
                                         └─────────┘
```

### Key Design Principles

1. **Separation of Concerns**: Clear separation between frontend UI, API layer, and data models
2. **Role-Based Access Control**: Comprehensive permission system based on user roles
3. **RESTful API Design**: Standard HTTP methods and status codes
4. **Token-Based Authentication**: Stateless authentication using Django REST Framework tokens
5. **Defensive Programming**: Extensive error handling and validation

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- Virtual environment tool (venv, conda, etc.)

### Initial Setup

1. **Clone and Setup Environment**
   ```bash
   git clone <repository-url>
   cd "Django User"
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Verify Installation**
   ```bash
   python ../testing/test_connection.py
   ```

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (for production)
DATABASE_URL=sqlite:///db.sqlite3

# API Configuration
API_BASE_URL=http://127.0.0.1:8000/api
API_TIMEOUT=10
API_RETRIES=3

# Logging
LOG_LEVEL=INFO
```

## Code Structure

### Backend Structure

```
backend/
├── config/              # Django project settings
│   ├── settings.py      # Main configuration
│   ├── urls.py         # Root URL configuration
│   ├── wsgi.py         # WSGI configuration
│   └── asgi.py         # ASGI configuration
├── apps/
│   └── Users/          # User management app
│       ├── models.py   # User model and roles
│       ├── views.py    # API endpoints
│       ├── serializers.py # Data validation
│       ├── urls.py     # URL routing
│       ├── admin.py    # Admin interface
│       └── migrations/ # Database migrations
└── manage.py           # Django management script
```

### Frontend Structure

```
frontend/
├── main.py             # Application entry point
├── models/
│   └── user.py         # Frontend user model
├── services/
│   └── services.py     # API communication
├── ui/                 # User interface components
│   ├── login_window.py
│   ├── register_window.py
│   └── dashboard.py
└── utils/
    └── validators.py   # Input validation
```

### Testing Structure

```
testing/
├── test_connection.py  # Backend connectivity test
├── populate.py         # Sample data creation
├── preview_db.py       # Database inspection
└── wipe_all.py         # Data cleanup
```

## Development Workflow

### Adding New Features

1. **Backend Development**
   ```bash
   # Create new migration if model changes
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   
   # Test API endpoints
   python manage.py runserver
   # Test with curl or Postman
   ```

2. **Frontend Development**
   ```bash
   # Test frontend connectivity
   python testing/test_connection.py
   
   # Run frontend application
   cd frontend
   python main.py
   ```

3. **Integration Testing**
   ```bash
   # Populate test data
   python testing/populate.py
   
   # Run full application test
   python frontend/main.py
   ```

### Code Quality Standards

1. **Python Style Guide**
   - Follow PEP 8 conventions
   - Use type hints where appropriate
   - Document all public methods and classes
   - Maximum line length: 100 characters

2. **Documentation Standards**
   - Comprehensive docstrings for all functions/classes
   - API endpoint documentation
   - User guide documentation
   - Code comments for complex logic

3. **Error Handling**
   - Always handle exceptions gracefully
   - Provide meaningful error messages
   - Log errors appropriately
   - Validate all user inputs

## Testing Guide

### Backend Testing

1. **Unit Tests**
   ```python
   # Example test for User model
   from django.test import TestCase
   from apps.Users.models import User, UserRole
   
   class UserModelTest(TestCase):
       def test_user_creation(self):
           user = User.objects.create_user(
               username='testuser',
               email='test@example.com',
               password='testpass123',
               role=UserRole.STUDENT
           )
           self.assertEqual(user.username, 'testuser')
           self.assertEqual(user.role, UserRole.STUDENT)
   ```

2. **API Testing**
   ```python
   # Example API test
   from rest_framework.test import APITestCase
   from rest_framework.authtoken.models import Token
   
   class UserAPITest(APITestCase):
       def setUp(self):
           self.user = User.objects.create_user(
               username='testuser',
               email='test@example.com',
               password='testpass123'
           )
           self.token = Token.objects.create(user=self.user)
   
       def test_login(self):
           response = self.client.post('/api/auth/login/', {
               'email': 'test@example.com',
               'password': 'testpass123'
           })
           self.assertEqual(response.status_code, 200)
   ```

3. **Running Tests**
   ```bash
   cd backend
   python manage.py test
   python manage.py test apps.Users.tests.UserModelTest
   ```

### Frontend Testing

1. **Manual Testing Checklist**
   - [ ] Login with valid credentials
   - [ ] Login with invalid credentials
   - [ ] User registration
   - [ ] Dashboard role-specific features
   - [ ] User management operations
   - [ ] Logout functionality

2. **Integration Testing**
   ```bash
   # Test backend connectivity
   python testing/test_connection.py
   
   # Populate test data
   python testing/populate.py
   
   # Test complete workflow
   python frontend/main.py
   ```

## API Design Patterns

### RESTful Conventions

1. **HTTP Methods**
   - GET: Retrieve data
   - POST: Create new resources
   - PUT/PATCH: Update existing resources
   - DELETE: Remove resources

2. **Status Codes**
   - 200: Success (GET)
   - 201: Created (POST)
   - 204: No Content (DELETE)
   - 400: Bad Request
   - 401: Unauthorized
   - 403: Forbidden
   - 404: Not Found

3. **URL Structure**
   ```
   /api/resource/           # Collection
   /api/resource/{id}/      # Individual item
   /api/resource/{id}/action/ # Action on item
   ```

### Response Format Standards

```json
// Success Response
{
    "success": true,
    "data": { ... },
    "message": "Optional success message"
}

// Error Response
{
    "success": false,
    "error": {
        "detail": "Error description",
        "field_errors": { ... }
    }
}
```

### Authentication Flow

```python
# Login Request
POST /api/auth/login/
{
    "email": "user@example.com",
    "password": "password"
}

# Response
{
    "message": "Login successful",
    "user": { ... },
    "token": "abc123..."
}

# Subsequent Requests
GET /api/users/
Headers: Authorization: Token abc123...
```

## Frontend Architecture

### PyQt6 Application Structure

1. **Main Application (`main.py`)**
   - Application lifecycle management
   - Window coordination
   - Signal/slot connections

2. **Services Layer (`services/`)**
   - API communication
   - Authentication management
   - Error handling

3. **UI Components (`ui/`)**
   - Login/Registration windows
   - Dashboard interface
   - User management forms

4. **Models (`models/`)**
   - Data structures
   - Business logic
   - Validation

### Signal/Slot Pattern

```python
# Window communication example
class LoginWindow(QWidget):
    login_success = pyqtSignal(User)
    switch_to_register = pyqtSignal()

# Connection in main app
self.login_window.login_success.connect(self.on_login_success)
self.login_window.switch_to_register.connect(self.show_register)
```

### Error Handling Strategy

```python
def api_call_with_error_handling(self):
    try:
        result = self.user_service.some_operation()
        if result['success']:
            # Handle success
            self.show_success_message(result['message'])
        else:
            # Handle API error
            self.show_error_message(result['error'])
    except Exception as e:
        # Handle unexpected error
        self.show_error_message(f"Unexpected error: {str(e)}")
        logger.exception("Unexpected error in operation")
```

## Security Implementation

### Authentication Security

1. **Token Management**
   - Tokens stored in memory only
   - Automatic token cleanup on logout
   - Token validation on each request

2. **Password Security**
   - Django's built-in password hashing
   - Password strength validation
   - Secure password change flow

3. **API Security**
   - CSRF protection disabled for API (token-based)
   - Input validation and sanitization
   - SQL injection prevention via ORM

### Authorization Patterns

```python
# Role-based access control
def check_user_permissions(user, action, target_user=None):
    if action == 'view_users':
        return user.role in ['admin', 'faculty', 'staff']
    elif action == 'modify_user':
        if user.role == 'admin':
            return True
        elif user.role == 'faculty' and target_user.role == 'student':
            return True
    return False
```

### Input Validation

```python
# Serializer validation example
class UserCreateSerializer(serializers.ModelSerializer):
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate_password(self, value):
        validate_password(value)  # Django's password validation
        return value
```

## Performance Considerations

### Database Optimization

1. **Query Optimization**
   ```python
   # Efficient queryset usage
   users = User.objects.select_related().filter(role='student')
   
   # Pagination for large datasets
   paginator = Paginator(users, 25)
   ```

2. **Indexing Strategy**
   ```python
   class User(AbstractUser):
       email = models.EmailField(unique=True, db_index=True)
       role = models.CharField(max_length=20, db_index=True)
   ```

### API Performance

1. **Response Optimization**
   - Minimal data in responses
   - Efficient serialization
   - Appropriate HTTP caching headers

2. **Error Handling**
   - Fast failure for invalid requests
   - Efficient validation
   - Proper logging without performance impact

### Frontend Performance

1. **UI Responsiveness**
   - Asynchronous API calls
   - Progress indicators
   - Efficient table updates

2. **Memory Management**
   - Proper widget cleanup
   - Event handler disconnection
   - Resource management

## Deployment Guide

### Development Deployment

```bash
# Backend
cd backend
python manage.py runserver 0.0.0.0:8000

# Frontend (separate terminal)
cd frontend
python main.py
```

### Production Considerations

1. **Django Settings**
   ```python
   # Production settings
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com']
   SECURE_SSL_REDIRECT = True
   SECURE_HSTS_SECONDS = 31536000
   ```

2. **Database**
   - Use PostgreSQL for production
   - Regular backups
   - Connection pooling

3. **Web Server**
   - Gunicorn + Nginx
   - Static file serving
   - SSL certificates

### Environment Setup

```bash
# Production dependencies
pip install gunicorn psycopg2-binary

# Static files collection
python manage.py collectstatic

# Database migration
python manage.py migrate --settings=config.settings.production
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   ```
   Problem: Frontend can't connect to backend
   Solution: 
   - Check if Django server is running
   - Verify API_BASE_URL configuration
   - Test with testing/test_connection.py
   ```

2. **Authentication Issues**
   ```
   Problem: Token authentication failing
   Solution:
   - Check token format in headers
   - Verify user is active
   - Ensure token hasn't been deleted
   ```

3. **Permission Errors**
   ```
   Problem: 403 Forbidden responses
   Solution:
   - Check user role permissions
   - Verify endpoint access rules
   - Review role-based filtering logic
   ```

### Debugging Tools

1. **Django Debug Toolbar**
   ```python
   # Add to development settings
   INSTALLED_APPS += ['debug_toolbar']
   MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
   ```

2. **Logging Configuration**
   ```python
   LOGGING = {
       'version': 1,
       'handlers': {
           'file': {
               'level': 'DEBUG',
               'class': 'logging.FileHandler',
               'filename': 'debug.log',
           },
       },
       'loggers': {
           'django': {
               'handlers': ['file'],
               'level': 'DEBUG',
           },
       },
   }
   ```

3. **API Testing Tools**
   - Postman for API testing
   - Django REST Framework browsable API
   - curl for command-line testing

### Performance Monitoring

1. **Database Queries**
   ```python
   from django.db import connection
   print(len(connection.queries))  # Number of queries
   ```

2. **Response Times**
   ```python
   import time
   start_time = time.time()
   # ... operation ...
   print(f"Operation took {time.time() - start_time:.2f} seconds")
   ```

## Contributing Guidelines

1. **Code Review Process**
   - All changes require code review
   - Test coverage for new features
   - Documentation updates

2. **Commit Standards**
   ```
   feat: Add user role management
   fix: Resolve login timeout issue
   docs: Update API documentation
   test: Add user model tests
   ```

3. **Branch Strategy**
   - `main`: Production-ready code
   - `develop`: Integration branch
   - `feature/*`: New features
   - `bugfix/*`: Bug fixes

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PyQt6 Documentation](https://doc.qt.io/qtforpython/)
- [Python PEP 8 Style Guide](https://pep8.org/)

---

This documentation should be updated as the system evolves. For questions or clarifications, please refer to the code comments or contact the development team.
