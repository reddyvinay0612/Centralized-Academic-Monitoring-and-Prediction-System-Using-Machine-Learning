@echo off
title CAMPS-ML Server Launcher
echo ===============================================================
echo  PESITM - Smart College Management System (CAMPS-ML)
echo ===============================================================
echo.

:: Prioritize direct real Python installation
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

echo [*] Terminating any existing node/python server processes on port 5000 / 5173...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
ping 127.0.0.1 -n 2 >nul

echo [*] Starting Flask Backend API on http://localhost:5000 ...
start "CAMPS Backend (Flask :5000)" cmd /k "cd /d %~dp0 && %PYTHON_CMD% run.py"

echo [*] Starting Vite Frontend on http://localhost:5173 ...
start "CAMPS Frontend (Vite :5173)" cmd /k "cd /d %~dp0frontend && npm run dev -- --host"

echo.
echo ===============================================================
echo  SUCCESS: Both servers launched in dedicated windows!
echo  - Frontend Portal:  http://localhost:5173
echo  - Backend API:      http://localhost:5000
echo ===============================================================
echo  You can leave those windows open while testing the application.
echo ===============================================================
