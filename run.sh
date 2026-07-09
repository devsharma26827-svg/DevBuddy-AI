#!/bin/bash

echo "=========================================="
echo "      ProjectPilot AI Startup Script      "
echo "=========================================="
echo ""

# 1. Check Python Installation
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python was not found on your system."
    echo "Please install Python 3.12 or newer."
    echo ""
    exit 1
fi

# 2. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo "[INFO] Virtual environment not found. Creating 'venv'..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment."
        exit 1
    fi
    echo "[SUCCESS] Virtual environment created successfully."
fi

# 3. Activate Virtual Environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment."
    exit 1
fi

# 4. Check/Install Dependencies
echo "[INFO] Checking and installing/updating dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies."
    exit 1
fi
echo "[SUCCESS] Dependencies are up to date."

# 5. Set up Environment Variables if not present
if [ ! -f ".env" ]; then
    echo "[INFO] .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "[WARNING] A template .env file has been created. Please configure your API keys in .env."
fi

# 6. Launch browser with delay, then start Flask server
echo ""
echo "[INFO] Launching ProjectPilot AI..."
echo "[INFO] Opening browser at http://127.0.0.1:5000"

# Open browser based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    (sleep 2 && open http://127.0.0.1:5000) &
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    (sleep 2 && xdg-open http://127.0.0.1:5000) &
fi

echo "[INFO] Running backend server..."
python backend.py
