#!/bin/bash

# YYS-SQR Build Script
# Builds the macOS application bundle

echo "Building YYS-SQR Application..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install py2app

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/

# Build application
echo "Building macOS application bundle..."
python setup.py py2app

echo "Build complete! Application available in dist/YYS-SQR.app"
echo ""
echo "To run the application:"
echo "  1. GUI: open dist/YYS-SQR.app"
echo "  2. CLI: python main.py"