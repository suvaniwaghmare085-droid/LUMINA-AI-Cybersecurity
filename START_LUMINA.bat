@echo off
cd /d "%~dp0backend"
if not exist ".venv\Scripts\python.exe" (
  echo Create the virtual environment and install requirements first.
  echo See README.md for setup instructions.
  pause
  exit /b 1
)
call .venv\Scripts\activate
python app.py
pause
