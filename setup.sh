#!/bin/bash

# Setup script for macOS/Linux

echo "Setting up Django User Management System..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
required_version="3.11"

if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo "Error: Python $required_version or higher is required. You have Python $python_version."
    exit 1
fi

echo "✓ Python $python_version detected"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Set up environment files
if [ ! -f "backend/.env" ]; then
    echo "Setting up backend environment file..."
    cp backend/.env.example backend/.env
    echo "✓ Backend .env file created"
else
    echo "✓ Backend .env file already exists"
fi

if [ ! -f "frontend/.env" ]; then
    echo "Setting up frontend environment file..."
    # Frontend .env already exists in the workspace
    echo "✓ Frontend .env file already exists"
fi

# Set up database
echo "Setting up database..."
cd backend
python manage.py migrate
echo "✓ Database migrations applied"

# Ask if user wants to create a superuser
read -p "Do you want to create a Django admin superuser? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

cd ..

echo
echo "✅ Setup complete!"
echo
echo "To start the application:"
echo "1. Backend: cd backend && python manage.py runserver"
echo "2. Frontend: python frontend/main.py"
echo
echo "Or run both with: ./start_app.sh"
