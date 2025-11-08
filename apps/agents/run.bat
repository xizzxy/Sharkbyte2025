@echo off
REM Activate venv and run the agents server

echo Activating virtual environment...
call ..\..\..\venv\Scripts\activate.bat

echo.
echo Starting CareerPilot AI Agents Server...
echo.
python main.py
