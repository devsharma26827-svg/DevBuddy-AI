@echo off
setlocal

echo ==========================================
echo       DevBuddy AI Startup Script      
echo ==========================================
echo.

set "ROOT_DIR=%~dp0"
set "VENV_PATH=%ROOT_DIR%venv"
set "BACKEND_PATH=%ROOT_DIR%backend"
set "FRONTEND_PATH=%ROOT_DIR%frontend"
set "VENV_PYTHON=%VENV_PATH%\Scripts\python.exe"
set "REQUIREMENTS_FILE=%BACKEND_PATH%\requirements.txt"
set "BACKEND_ENTRY=%BACKEND_PATH%\backend.py"

if not exist "%BACKEND_PATH%\" (
    echo [ERROR] Backend folder was not found at "%BACKEND_PATH%".
    pause
    exit /b 1
)

if not exist "%FRONTEND_PATH%\" (
    echo [ERROR] Frontend folder was not found at "%FRONTEND_PATH%".
    pause
    exit /b 1
)

if not exist "%REQUIREMENTS_FILE%" (
    echo [ERROR] Requirements file was not found at "%REQUIREMENTS_FILE%".
    pause
    exit /b 1
)

if not exist "%BACKEND_ENTRY%" (
    echo [ERROR] Backend entry point was not found at "%BACKEND_ENTRY%".
    pause
    exit /b 1
)

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
if not exist "%VENV_PATH%\" (
    echo [INFO] Virtual environment not found. Creating 'venv'...
    "%PYTHON_CMD%" -m venv "%VENV_PATH%"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created successfully.
)

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Virtual environment Python was not found at "%VENV_PYTHON%".
    pause
    exit /b 1
)

:: 3. Verify Virtual Environment
echo [INFO] Using virtual environment Python...
"%VENV_PYTHON%" --version
if %errorlevel% neq 0 (
    echo [ERROR] Failed to run virtual environment Python.
    pause
    exit /b 1
)

:: 4. Check/Install Dependencies
echo [INFO] Checking and installing/updating dependencies...
"%VENV_PYTHON%" -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [ERROR] Failed to upgrade pip.
    pause
    exit /b 1
)
"%VENV_PYTHON%" -m pip install -r "%REQUIREMENTS_FILE%"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies are up to date.

:: 5. Set up Environment Variables if not present
if not exist "%ROOT_DIR%.env" (
    echo [INFO] .env file not found. Copying from .env.example...
    copy "%ROOT_DIR%.env.example" "%ROOT_DIR%.env" >nul
    echo [WARNING] A template .env file has been created. Please configure your API keys in .env.
)

:: 6. Launch browser with delay, then start Flask server
echo.
echo [INFO] Launching ProjectPilot AI...
echo [INFO] Opening browser at http://127.0.0.1:5000
start /b cmd /c "ping -n 3 127.0.0.1 >nul && start http://127.0.0.1:5000"

echo [INFO] Running backend server...
"%VENV_PYTHON%" "%BACKEND_ENTRY%"

pause
