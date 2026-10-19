@echo off
rem Start the Drone Threat Trainer on Windows.
rem   start.bat           first run creates .venv and installs requirements (needs internet once)
rem   start.bat --demo    also seeds a demo cohort if there is no database yet
rem Any other arguments go to run.py, for example start.bat --port 8000 --lan
rem NO_BROWSER=1 start.bat skips opening the browser.
setlocal enabledelayedexpansion
cd /d "%~dp0"

set DEMO=0
set ARGS=
set PORT=5050
set NEXT_PORT=0

:loop
if "%~1"=="" goto done_args
if "%~1"=="--demo" (
  set DEMO=1
  shift
  goto loop
)
if "%~1"=="--port" (
  set NEXT_PORT=1
  set ARGS=!ARGS! %1
  shift
  goto loop
)
if "!NEXT_PORT!"=="1" (
  set PORT=%~1
  set NEXT_PORT=0
  set ARGS=!ARGS! %1
  shift
  goto loop
)
set ARGS=!ARGS! %1
shift
goto loop

:done_args
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

if not "%NO_BROWSER%"=="1" start "" "http://localhost:!PORT!/mission"
".venv\Scripts\python.exe" run.py !ARGS!
