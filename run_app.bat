@echo off
title CAMPS-ML Web Server
echo =====================================================================
echo Starting CAMPS-ML Development Server on http://127.0.0.1:5000
echo =====================================================================

where python >nul 2>&1
if exist "C:\Users\vinay\anaconda3\python.exe" (
    "C:\Users\vinay\anaconda3\python.exe" run.py
) else (
    py run.py
)
pause
