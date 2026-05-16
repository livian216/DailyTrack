@echo off
setlocal

set "FULL_CLEAN=0"
if /I "%~1"=="--all" set "FULL_CLEAN=1"

if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__
for /d /r %%D in (__pycache__) do @if exist "%%D" rmdir /s /q "%%D"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
del /q *.spec 2>nul
if exist tmp_test.db del /q tmp_test.db
if exist tmp_test.db-journal del /q tmp_test.db-journal
if exist .test_tmp rmdir /s /q .test_tmp

if "%FULL_CLEAN%"=="1" (
  if exist dist rmdir /s /q dist
  if exist installer_output rmdir /s /q installer_output
  echo [OK] Full clean done: build/cache/spec and dist/installer_output removed.
) else (
  echo [OK] Safe clean done: build/cache/spec removed, dist/installer_output kept.
)

echo [INFO] User data under %%APPDATA%%\DailyTrack is preserved.
