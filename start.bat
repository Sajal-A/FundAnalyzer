@echo off
REM Start both Backend API and Frontend UI in separate windows
REM Usage: Run this batch file to start the entire application

cls
color 0A
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║     Fund Performance Diagnostic AI - Full Stack Startup       ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Get the project root directory
set PROJECT_ROOT=%~dp0

REM Check if running from the right directory
if not exist "%PROJECT_ROOT%\main.py" (
    echo ERROR: Could not find main.py. Make sure to run this from the project root.
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo ✓ Python found

echo.
echo [2/4] Checking dependencies...
pip list | find "fastapi" >nul
if errorlevel 1 (
    echo WARNING: Some dependencies may be missing
    echo Run: pip install -r requirements.txt
)
pip list | find "streamlit" >nul
if errorlevel 1 (
    echo WARNING: Streamlit not found
    echo Run: pip install -r frontend/requirements.txt
)
echo ✓ Main dependencies found

echo.
echo [3/4] Starting Backend API...
start "Fund Performance Diagnostic - Backend API" cmd /k "cd /d %PROJECT_ROOT% && python main.py"
echo ✓ Backend starting in new window

timeout /t 3 /nobreak

echo.
echo [4/4] Starting Frontend UI...
start "Fund Performance Diagnostic - Frontend UI" cmd /k "cd /d %PROJECT_ROOT%\frontend && streamlit run app.py"
echo ✓ Frontend starting in new window

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    Startup Complete                           ║
echo ╠════════════════════════════════════════════════════════════════╣
echo ║                                                                ║
echo ║  Backend API:  http://localhost:8000                          ║
echo ║  API Docs:     http://localhost:8000/docs                     ║
echo ║  Frontend UI:  http://localhost:8501                          ║
echo ║                                                                ║
echo ║  Close these windows to stop the application                  ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

pause
