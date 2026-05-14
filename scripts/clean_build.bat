@echo off
setlocal
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist installer_output rmdir /s /q installer_output
del /q *.spec 2>nul
echo [OK] Build artifacts cleaned. User data under %%APPDATA%%\DailyTrack is preserved.
