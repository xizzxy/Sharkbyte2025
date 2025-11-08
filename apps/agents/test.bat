@echo off
REM Activate venv and run environment test

echo Activating virtual environment...
call ..\..\..\venv\Scripts\activate.bat

echo.
echo Testing environment configuration...
echo.
python test_env.py
pause
