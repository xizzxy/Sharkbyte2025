@echo off
echo ============================================================
echo    CareerPilot AI - Starting All Services
echo ============================================================
echo.
echo This will open 2 windows:
echo   1. Python Agents Backend (port 8000)
echo   2. Next.js Frontend (port 3000)
echo.
echo Press any key to continue...
pause > nul

echo.
echo Starting Backend...
start "CareerPilot Backend" cmd /k "cd /d C:\Users\xizzy\Sharkbyte2025 && venv\Scripts\activate && cd careerpilot\apps\agents && python main.py"

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo Starting Frontend...
start "CareerPilot Frontend" cmd /k "cd /d C:\Users\xizzy\Sharkbyte2025\careerpilot\apps\web && npm run dev"

echo.
echo ============================================================
echo    Both services are starting!
echo ============================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
pause > nul
