#!/bin/bash

# FoodAI - Installation Script

echo "====================================="
echo "FoodAI Installation Script"
echo "====================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✓ Python $python_version detected"
else
    echo "✗ Python 3.8 or higher is required"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "✗ Failed to create virtual environment"
    exit 1
fi
echo "✓ Virtual environment created"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "✗ Failed to install dependencies"
    exit 1
fi
echo "✓ Dependencies installed"

# Create necessary directories
echo "Creating directories..."
mkdir -p deep_learning/data database models static/uploads logs

# Create sample dataset
echo "Creating sample dataset..."
python deep_learning/data/create_dataset.py

if [ $? -ne 0 ]; then
    echo "✗ Failed to create dataset"
    exit 1
fi
echo "✓ Sample dataset created"

# Initialize database
echo "Initializing database..."
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database initialized')
"

if [ $? -ne 0 ]; then
    echo "✗ Failed to initialize database"
    exit 1
fi
echo "✓ Database initialized"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///food_recommendation.db

# Model Paths
MODEL_PATH=models/food_recommender.h5
SCALER_PATH=models/scaler.pkl
ENCODER_PATH=models/label_encoders.pkl

# Application Settings
APP_NAME=FoodAI
APP_VERSION=1.0.0
MAX_RECOMMENDATIONS=20
MEAL_PLAN_DAYS=7

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
EOF
    echo "✓ .env file created"
fi

# Train initial model (optional)
read -p "Do you want to train the initial model? (y/n): " train_model
if [[ $train_model =~ ^[Yy]$ ]]; then
    echo "Training initial model..."
    python deep_learning/train_model.py
    
    if [ $? -ne 0 ]; then
        echo "⚠ Model training had issues, but continuing..."
    else
        echo "✓ Model trained successfully"
    fi
fi

echo ""
echo "====================================="
echo "Installation Complete!"
echo "====================================="
echo ""
echo "To start the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the application: python app.py"
echo "3. Open browser: http://localhost:5000"
echo ""
echo "Default admin credentials:"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "====================================="