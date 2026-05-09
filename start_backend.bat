@echo off
REM Start only the Backend API

cls
color 0A
echo.
echo Starting Fund Performance Diagnostic AI - Backend API...
echo.
echo Backend API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

cd /d %~dp0
python main.py

pause
