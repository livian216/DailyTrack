@echo off
setlocal
where python >nul 2>nul
if %errorlevel% neq 0 (
  echo [ERROR] Python not found. Please install Python 3 first.
  exit /b 1
)
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [OK] Development environment ready.
