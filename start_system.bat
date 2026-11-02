@echo off
title CAMPS-ML System Launcher
color 0B
echo ===============================================================================
echo   PESITM SHIVAMOGGA - SMART COLLEGE MANAGEMENT & ACADEMIC PREDICTION SYSTEM
echo                 Centralized Academic Monitoring (CAMPS-ML)
echo ===============================================================================
echo.
echo [1/3] Verifying runtime dependencies...
where py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python launcher 'py' not found in PATH!
    pause
    exit /b 1
)

where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js package manager 'npm' not found in PATH!
    pause
    exit /b 1
)

echo [OK] Python and Node.js detected.
echo.
echo [2/3] Starting Backend REST API Server (Flask on http://localhost:5000)...
start "CAMPS-ML Backend API (Port 5000)" cmd /k "color 0A && py run.py"

echo [3/3] Starting Frontend React Application (Vite on http://localhost:5173)...
start "CAMPS-ML Frontend UI (Port 5173)" cmd /k "color 0E && cd frontend && npm run dev"

echo.
echo ===============================================================================
echo                    SYSTEM LAUNCHED SUCCESSFULLY!
echo ===============================================================================
echo   Frontend Application: http://localhost:5173
echo   Backend REST API:     http://localhost:5000/api/health
echo ===============================================================================
echo.
echo   DEMO CREDENTIALS CHEAT-SHEET:
echo   -----------------------------------------------------------------------------
echo   Role       | Identifier / Email          | Password    | Portal Route
echo   -----------------------------------------------------------------------------
echo   Principal  | principal@pesitm.edu        | password123 | /login/principal
echo   Admin      | admin@pesitm.edu            | password123 | /login/admin
echo   Teacher    | anita.rao@pesitm.edu        | password123 | /login/teacher
echo   Student    | 4PM21CS001                  | password123 | /login/student
echo   Parent     | parent_001@gmail.com        | password123 | /login/parent
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
