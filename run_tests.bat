@echo off
title CAMPS-ML Automated Test Runner
echo =====================================================================
echo Running Smart College / CAMPS-ML Full Test Suite
echo =====================================================================
echo.
echo [1/2] Running Backend Security & API Pytest Matrix (73 Tests)...
py -m pytest backend/tests/ -v
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Backend tests encountered failures!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Running Frontend Vitest Unit Tests...
npm run test:frontend
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Frontend tests encountered failures!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo =====================================================================
echo [SUCCESS] ALL 73 Backend Tests and Frontend Tests Passed!
echo =====================================================================
pause
