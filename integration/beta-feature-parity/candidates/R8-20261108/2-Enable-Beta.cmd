@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-SEST-Beta.ps1" -Action Enable
if errorlevel 1 echo Script stopped. Copy the error above into the chat.
pause
