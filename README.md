# Django User Management System

A full-stack user management application with a Django REST API backend and PyQt6 desktop frontend.

## Features

- User authentication (login/register)
- Role-based access control (Admin, Student, Faculty, Staff)
- REST API backend with Django
- Desktop GUI frontend with PyQt6
- Token-based authentication
- SQLite database (development)

## Project Structure

```
├── backend/                  # Django REST API
│   ├── apps/
│   │   └── Users/           # User management app
│   ├── config/              # Django settings
│   └── manage.py
├── frontend/                # PyQt6 desktop application
│   ├── ui/                  # User interface components
│   ├── services/            # API communication
│   ├── models/              # Data models
│   └── main.py             # Application entry point
├── testing/                 # Utility scripts
│   ├── test_connection.py   # Backend connectivity test
│   ├── populate.py          # Sample data population
│   ├── preview_db.py        # Database viewer
│   └── wipe_all.py          # Data cleanup
├── requirements.txt         # Python dependencies
├── start_app.bat           # Windows startup script
├── start_app.sh            # Unix startup script
├── setup.bat               # Windows setup script
├── setup.sh                # Unix setup script
└── .env.example            # Environment variables template
```

## Prerequisites

- Python 3.11 or higher
- Git

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repository-url>
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
