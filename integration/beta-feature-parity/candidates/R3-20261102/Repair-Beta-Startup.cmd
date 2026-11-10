@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Repair-SEST-Beta-Startup.ps1" -Action Repair
if errorlevel 1 echo Repair stopped. Copy the error above into chat.
pause
