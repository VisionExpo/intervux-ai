@echo off
echo ====================================
echo Intervux AI - Development Server
echo ====================================

:: Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found in .\venv
    echo Please create it using: python -m venv venv
    exit /b 1
)

:: Activate background components (Redis, Celery if applicable)
echo [1/3] Note: Make sure Redis is running.

:: Activate python venv
echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

:: Start backend (FastAPI)
echo [3/3] Starting FastAPI Backend on port 8000...
start cmd /k "cd backend && uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

:: Start frontend (Vite)
echo [4/3] Starting Vite Frontend on port 5173...
start cmd /k "cd frontend && npm run dev"

echo Development servers are starting in separate windows.
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:8000/docs
