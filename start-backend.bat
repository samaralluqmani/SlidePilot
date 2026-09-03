@echo off
cd /d "%~dp0backend"
if not exist venv\Scripts\activate.bat (
  echo Backend virtual environment not found.
  echo Run: python -m venv venv
  pause
  exit /b 1
)
call venv\Scripts\activate.bat
uvicorn main:app --reload
