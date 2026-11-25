@echo off
title CAMPS-ML System Launcher
color 0B
set "PATH=C:\Users\vinay\AppData\Local\Python\bin;C:\Users\vinay\AppData\Local\Python\pythoncore-3.14-64\Scripts;%PATH%"

set PYTHON_CMD=python
if exist "C:\Users\vinay\AppData\Local\Python\bin\python.exe" (
    set PYTHON_CMD="C:\Users\vinay\AppData\Local\Python\bin\python.exe"
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    )
)
echo ===============================================================================
echo   PESITM SHIVAMOGGA - SMART COLLEGE MANAGEMENT & ACADEMIC PREDICTION SYSTEM
echo                 Centralized Academic Monitoring (CAMPS-ML)
echo ===============================================================================
echo.
echo [1/4] Verifying runtime dependencies...
where py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where python >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python launcher ('py' or 'python') not found in PATH!
        echo Please install Python 3.10+ from python.org and add it to PATH.
        pause
        exit /b 1
    )
)

where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js package manager 'npm' not found in PATH!
    echo Please install Node.js from nodejs.org and add it to PATH.
    pause
    exit /b 1
)

echo [OK] Python and Node.js detected.
echo.

echo [2/4] Checking package installations & database readiness...
if not exist "frontend\node_modules\" (
    echo [*] Frontend dependencies not found. Installing node packages (one-time setup)...
    cd frontend && call npm install && cd ..
)

py -c "import flask, flask_jwt_extended, flask_cors, flask_bcrypt" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [*] Python packages missing. Installing requirements from requirements.txt...
    py -m pip install -r requirements.txt
)

echo.
echo [3/4] Starting Backend REST API Server (Flask on http://localhost:5000)...
start "CAMPS-ML Backend API (Port 5000)" cmd /k "color 0A && py run.py"

echo [4/4] Starting Frontend React Application (Vite on http://localhost:5173)...
start "CAMPS-ML Frontend UI (Port 5173)" cmd /k "color 0E && cd frontend && npm run dev"

echo.
echo ===============================================================================
echo                    SYSTEM LAUNCHED SUCCESSFULLY!
echo ===============================================================================
echo   Frontend Application: http://localhost:5173
echo   Backend REST API:     http://localhost:5000/api/health
echo ===============================================================================
echo.
echo   UNIVERSAL CREDENTIALS CHEAT-SHEET (Works for everyone out of the box):
echo   -----------------------------------------------------------------------------
echo   Role       ^| Identifier / Email          ^| Password    ^| Portal Route
echo   -----------------------------------------------------------------------------
echo   Principal  ^| principal@pesitm.edu        ^| password123 ^| /login/principal
echo   Admin      ^| admin@pesitm.edu            ^| password123 ^| /login/admin
echo   Teacher    ^| anita.rao@pesitm.edu        ^| password123 ^| /login/teacher
echo   Teacher ID ^| EMP-CSE-01                  ^| password123 ^| /login/teacher
echo   Student    ^| 4PM23CS071                  ^| password123 ^| /login/student
echo   Student    ^| 4PM21CS001                  ^| password123 ^| /login/student
echo   Parent     ^| parent_4pm23cs071           ^| password123 ^| /login/parent
echo   Parent     ^| parent_001@gmail.com        ^| password123 ^| /login/parent
echo   -----------------------------------------------------------------------------
echo.
echo Opening browser at http://localhost:5173 in 3 seconds...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo Both servers are actively running in their respective command windows.
echo To stop the system, simply close those two command prompt windows.
echo.
pause
