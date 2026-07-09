@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo       ProjectPilot AI Startup Script      
echo ==========================================
echo.

:: 1. Check Python Installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python was not found on your system.
        echo Please install Python 3.12 or newer from https://www.python.org/
        echo Make sure to check the option "Add Python to PATH" during installation.
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

:: 2. Setup Virtual Environment
if not exist venv (
    echo [INFO] Virtual environment not found. Creating 'venv'...
    !PYTHON_CMD! -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created successfully.
)

:: 3. Activate Virtual Environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: 4. Check/Install Dependencies
echo [INFO] Checking and installing/updating dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies are up to date.

:: 5. Set up Environment Variables if not present
if not exist .env (
    echo [INFO] .env file not found. Copying from .env.example...
    copy .env.example .env >nul
    echo [WARNING] A template .env file has been created. Please configure your API keys in .env.
)

:: 6. Launch browser with delay, then start Flask server
echo.
echo [INFO] Launching ProjectPilot AI...
echo [INFO] Opening browser at http://127.0.0.1:5000
start /b cmd /c "ping -n 3 127.0.0.1 >nul && start http://127.0.0.1:5000"

echo [INFO] Running backend server...
python backend.py

pause
