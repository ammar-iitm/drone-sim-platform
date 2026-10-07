@echo off
rem Start the Drone Threat Trainer on Windows.
rem   start.bat           first run creates .venv and installs requirements (needs internet once)
rem   start.bat --demo    also seeds a demo cohort if there is no database yet
setlocal
cd /d "%~dp0"

set DEMO=0
if "%~1"=="--demo" (
  set DEMO=1
  shift
)

if not exist ".venv\Scripts\python.exe" (
  echo First run: creating .venv and installing requirements...
  py -3 -m venv .venv 2>nul || python -m venv .venv
  if errorlevel 1 (
    echo Python 3.10 or newer is needed. Install it from python.org and tick "Add to PATH".
    exit /b 1
  )
  ".venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
  ".venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt
)

if "%DEMO%"=="1" if not exist "data\trainer.db" ".venv\Scripts\python.exe" scripts\seed_demo.py

start "" http://localhost:5050/mission
".venv\Scripts\python.exe" run.py %1 %2 %3 %4
