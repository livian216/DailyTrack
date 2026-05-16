@echo off
setlocal
if not exist dist\DailyTrack (
  echo [ERROR] dist\DailyTrack not found. Run scripts\build_exe.bat first.
  exit /b 1
)
where ISCC.exe >nul 2>nul
if %errorlevel% neq 0 (
  echo [ERROR] ISCC.exe not found.
  echo Please install Inno Setup and add ISCC.exe to PATH.
  exit /b 1
)
if not exist installer_output mkdir installer_output
ISCC.exe installer\DailyTrack.iss
if %errorlevel% neq 0 (
  echo [ERROR] Inno Setup compile failed.
  exit /b 1
)
echo [OK] Installer output: installer_output\DailyTrack_Setup_v1.1.0.exe

