#!/bin/bash

echo "🚀 Starting CampusConnect Backend"
echo "=================================="

# Function to find a compatible Python version
find_python() {
    for python_cmd in python3.12 python3.11 python3.10 python3; do
        if command -v $python_cmd &> /dev/null; then
            version=$($python_cmd --version 2>&1 | cut -d' ' -f2)
            major=$(echo $version | cut -d'.' -f1)
            minor=$(echo $version | cut -d'.' -f2)
            
            # Check if version is between 3.8 and 3.12
            if [[ $major -eq 3 && $minor -ge 8 && $minor -le 12 ]]; then
                echo "✅ Found compatible Python: $python_cmd ($version)"
                echo $python_cmd
                return 0
            fi
        fi
    done
    
    echo "❌ No compatible Python version found (need 3.8-3.12)"
    echo "   Current system Python might be too new (3.13+)"
    echo "   Please install Python 3.11 or 3.12"
    return 1
}

# Find compatible Python
PYTHON_CMD=$(find_python)
if [ $? -ne 0 ]; then
    exit 1
fi

# Remove existing venv if it exists but is broken
if [ -d "venv" ] && [ ! -f "venv/bin/activate" ]; then
    echo "🗑️  Removing broken virtual environment..."
    rm -rf venv
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv venv
    
    if [ ! -f "venv/bin/activate" ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if activation worked
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip first
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    echo "🔧 You may need to install some system dependencies"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "✏️  Please edit .env with your configuration"
fi

# Start the server
echo "🎯 Starting FastAPI server..."
echo "📚 API Documentation will be available at: http://localhost:8000/docs"
echo "🌐 Frontend should connect to: http://localhost:8000"
echo ""

python run.py
