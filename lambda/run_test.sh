#!/bin/bash
# Simple bash script to run and practice bash scripting

echo "============================================"
echo "Banking Transaction Pipeline - API Test"
echo "============================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo ""
    echo "Please create a .env file with your OBP credentials."
    echo "You can copy env.example as a template."
    echo ""
    exit 1
fi

# Check if virtual environment exists
if [ ! -d venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run test
echo ""
echo "Running test script..."
echo ""
python test_fetch_data.py

echo ""
echo "============================================"
echo "Test complete!"
echo "============================================"

