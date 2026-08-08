@echo off
echo.
echo  ============================================================
echo   Personalized Interview Preparation System - Backend Server
echo  ============================================================
echo.
echo  Starting FastAPI server on http://127.0.0.1:8000
echo  API Docs: http://127.0.0.1:8000/docs
echo.
echo  Press Ctrl+C to stop the server.
echo.
cd /d "%~dp0backend"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
