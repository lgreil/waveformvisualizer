@echo off
echo Music Waveform Visualizer
echo ========================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking and installing requirements...
pip install -r requirements.txt

REM Run the visualizer
echo.
echo Running the visualizer...
python generate_waveform.py %*

pause 