@echo off
REM Start only the Frontend UI

cls
color 0A
echo.
echo Starting Fund Performance Diagnostic AI - Frontend UI...
echo.
echo Frontend UI will be available at: http://localhost:8501
echo.
echo Make sure the backend is running!
echo.

cd /d %~dp0\frontend
streamlit run app.py

pause
