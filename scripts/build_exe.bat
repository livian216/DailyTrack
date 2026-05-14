@echo off
setlocal
if not exist .venv\Scripts\activate (
  echo [ERROR] .venv not found. Run scripts\setup_env.bat first.
  exit /b 1
)
call .venv\Scripts\activate
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
pyinstaller --noconfirm --clean --windowed --name DailyTrack main.py
echo [OK] Build output: dist\DailyTrack\
