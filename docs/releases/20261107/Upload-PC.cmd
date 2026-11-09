@echo off
setlocal
set "POWERSHELL_TELEMETRY_OPTOUT=1"
set "DOTNET_CLI_TELEMETRY_OPTOUT=1"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Upload-PC.ps1"
set "sestExitCode=%ERRORLEVEL%"
if not "%sestExitCode%"=="0" echo Script stopped. Keep the error above for review.
pause
exit /b %sestExitCode%
