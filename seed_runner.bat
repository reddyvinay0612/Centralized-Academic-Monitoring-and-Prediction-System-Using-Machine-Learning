@echo off
title CAMPS-ML Database Seeder & Initializer
echo =====================================================================
echo  PESITM Smart College / CAMPS-ML Database Initialization
echo =====================================================================
echo.
echo Initializing normalized SQLite database with:
echo  - 4 Academic Departments (CSE, ISE, ECE, CSD)
echo  - 12 Classes & Semesters
echo  - 12 Faculty members & HoDs
echo  - 240 VTU Students
echo  - 200 Linked Parents & Guardians
echo  - VTU CIE Marks, Attendance, Risk Predictions & SHAP Attributions
echo.
py backend/init_db.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Database initialization failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo =====================================================================
echo [SUCCESS] Database Seeded Successfully (backend/camps_smart_college.db)
echo =====================================================================
pause
