@echo off
echo Starting Django User Management System...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please create a virtual environment first:
    echo python -m venv venv
    echo venv\Scripts\activate
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Test Django backend connection
echo Testing Django backend connection...
python testing/test_connection.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Django backend is not running. Starting it now...
    echo.
    
    REM Start Django backend in a new window
    start "Django Backend" cmd /k "cd backend && python manage.py runserver"
    
    REM Wait a few seconds for Django to start
    timeout /t 5 /nobreak >nul
    
    REM Test connection again
    python testing/test_connection.py
)

if %ERRORLEVEL% equ 0 (
    echo.
    echo Backend is ready! Starting frontend...
    echo.
    
    REM Start frontend
    python frontend/main.py
) else (
    echo.
    echo Failed to start Django backend. Please check the error messages above.
    pause
)
