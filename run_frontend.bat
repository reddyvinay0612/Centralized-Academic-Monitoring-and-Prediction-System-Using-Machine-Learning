@echo off
title CAMPS-ML Vite Frontend UI
color 0E
echo [*] Starting Vite Frontend on http://localhost:5173 ...
cd /d "%~dp0frontend"
npm run dev -- --host
pause
