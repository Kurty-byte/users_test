@echo off
echo Setting up Django User Management System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

echo Python detected: 
python --version

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed

REM Set up environment files
if not exist "backend\.env" (
    echo Setting up backend environment file...
    copy "backend\.env.example" "backend\.env"
    echo Backend .env file created
) else (
    echo Backend .env file already exists
)

if not exist "frontend\.env" (
    echo Frontend .env file already exists
)

REM Set up database
echo Setting up database...
cd backend
python manage.py migrate
echo Database migrations applied

REM Ask if user wants to create a superuser
set /p create_superuser="Do you want to create a Django admin superuser? (y/n): "
if /i "%create_superuser%"=="y" (
    python manage.py createsuperuser
)

cd ..

echo.
echo Setup complete!
echo.
echo To start the application:
echo 1. Backend: cd backend ^&^& python manage.py runserver
echo 2. Frontend: python frontend/main.py
echo.
echo Or run: start_app.bat
echo.
pause
