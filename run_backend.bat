@echo off
title CAMPS-ML Flask Backend API
color 0A
set "PATH=C:\Users\vinay\AppData\Local\Python\bin;C:\Users\vinay\AppData\Local\Python\pythoncore-3.14-64\Scripts;%PATH%"

set PYTHON_CMD=python
if exist "C:\Users\vinay\AppData\Local\Python\bin\python.exe" (
    set PYTHON_CMD="C:\Users\vinay\AppData\Local\Python\bin\python.exe"
)

echo [*] Starting Flask Backend API on http://localhost:5000 ...
cd /d "%~dp0"
%PYTHON_CMD% run.py
pause
