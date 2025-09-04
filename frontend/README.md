# PyQt6 Application

This project is a PyQt6 application that includes a simple login, registration, and dashboard interface. It is designed to be integrated with a Django backend for user management in the future.

## Project Structure

```
pyqt6-app
├── src
│   ├── main.py                # Entry point of the application
│   ├── ui                     # Contains UI components
│   │   ├── __init__.py        # Package initialization
│   │   ├── login_window.py     # Login window UI
│   │   ├── register_window.py  # Registration window UI
│   │   └── dashboard_window.py  # Dashboard window UI
│   ├── services                # Contains service logic
│   │   ├── __init__.py        # Package initialization
│   │   └── auth_service.py     # Authentication service
│   ├── models                  # Contains data models
│   │   ├── __init__.py        # Package initialization
│   │   └── user.py            # User model
│   └── utils                  # Contains utility functions
│       ├── __init__.py        # Package initialization
│       └── validators.py       # Input validation functions
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd pyqt6-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/main.py
   ```

## Usage Guidelines

- The application starts with the login page. Users can enter their credentials to log in.
- If the user does not have an account, they can navigate to the registration page to create one.
- After logging in, users will be directed to the dashboard, where they can view their information and navigate to other sections.

## Future Integration

This application is designed to connect with a Django backend for user management. The `auth_service.py` file will handle the communication with the backend for authentication processes, including login and registration.

## License

This project is licensed under the MIT License.