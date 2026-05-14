@echo off
setlocal
if not exist .venv\Scripts\activate (
  echo [ERROR] .venv not found. Run scripts\setup_env.bat first.
  exit /b 1
)
call .venv\Scripts\activate
python main.py
