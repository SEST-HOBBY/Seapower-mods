@echo off
rem SEST Integration Pack - turn the SEST beta features back on after "turn off"
rem or "remove", then run the normal SETUP. Quit Sea Power first.
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0sest-setup.ps1" -FromCmd -BetaFeatures On
if errorlevel 1 pause
