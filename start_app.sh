#!/bin/bash

# Startup script for macOS/Linux

echo "Starting Django User Management System..."
echo

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run setup.sh first:"
    echo "./setup.sh"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Test Django backend connection
echo "Testing Django backend connection..."
python testing/test_connection.py

if [ $? -ne 0 ]; then
    echo
    echo "Django backend is not running. Starting it now..."
    echo
    
    # Start Django backend in background
    cd backend
    python manage.py runserver &
    DJANGO_PID=$!
    cd ..
    
    # Wait a few seconds for Django to start
    sleep 5
    
    # Test connection again
    python testing/test_connection.py
fi

if [ $? -eq 0 ]; then
    echo
    echo "Backend is ready! Starting frontend..."
    echo
    
    # Start frontend
    python frontend/main.py
    
    # Kill Django process when frontend closes (if we started it)
    if [ ! -z "$DJANGO_PID" ]; then
        echo "Stopping Django backend..."
        kill $DJANGO_PID 2>/dev/null
    fi
else
    echo
    echo "Failed to start Django backend. Please check the error messages above."
fi
