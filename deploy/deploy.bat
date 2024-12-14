@echo off
REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

REM Check if virtual environment directory exists
IF NOT EXIST venv (
    echo Virtual environment directory 'venv' not found.
    echo Creating virtual environment...
    python -m venv venv
) ELSE (
    echo Virtual environment directory 'venv' found.
)

REM Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install required libraries
echo Installing required libraries...
pip install -r requirements.txt

REM Run the cron job scheduler
echo Running cron job scheduler...
python cron_job_scheduler.py

REM Deactivate the virtual environment
echo Deactivating virtual environment...
call venv\Scripts\deactivate

echo Deployment complete.