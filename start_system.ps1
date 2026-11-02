# ===============================================================================
#   PESITM SHIVAMOGGA - SMART COLLEGE MANAGEMENT & ACADEMIC PREDICTION SYSTEM
#                 Centralized Academic Monitoring (CAMPS-ML)
# ===============================================================================

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "   PESITM SHIVAMOGGA - SMART COLLEGE MANAGEMENT & ACADEMIC PREDICTION SYSTEM   " -ForegroundColor Cyan
Write-Host "                 Centralized Academic Monitoring (CAMPS-ML)                    " -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

# Verify Python
if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python launcher 'py' not found in PATH!" -ForegroundColor Red
    exit 1
}

# Verify npm
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Node.js package manager 'npm' not found in PATH!" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Runtime prerequisites detected." -ForegroundColor Green
Write-Host ""

Write-Host "[1/2] Launching Backend REST API Server (Flask on http://localhost:5000)..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList '/k "color 0A && py run.py"'

Write-Host "[2/2] Launching Frontend Application Server (Vite on http://localhost:5173)..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList '/k "color 0E && cd frontend && npm run dev"'

Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host "                    SYSTEM LAUNCHED SUCCESSFULLY!                              " -ForegroundColor Green
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host "  Frontend URL:     http://localhost:5173" -ForegroundColor White
Write-Host "  Backend Health:   http://localhost:5000/api/health" -ForegroundColor White
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  DEMO CREDENTIALS CHEAT-SHEET:" -ForegroundColor Magenta
Write-Host "  -----------------------------------------------------------------------------" -ForegroundColor Gray
Write-Host "  Principal  | principal@pesitm.edu     | password123 | /login/principal" -ForegroundColor White
Write-Host "  Admin      | admin@pesitm.edu         | password123 | /login/admin" -ForegroundColor White
Write-Host "  Teacher    | anita.rao@pesitm.edu     | password123 | /login/teacher" -ForegroundColor White
Write-Host "  Student    | 4PM21CS001               | password123 | /login/student" -ForegroundColor White
Write-Host "  Parent     | parent_001@gmail.com     | password123 | /login/parent" -ForegroundColor White
Write-Host "  -----------------------------------------------------------------------------" -ForegroundColor Gray
Write-Host ""

Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"

Write-Host "Both servers are running in separate terminal windows." -ForegroundColor Cyan
Write-Host "Close those terminal windows when you wish to terminate the servers." -ForegroundColor Cyan
