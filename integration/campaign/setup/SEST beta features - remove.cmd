@echo off
rem SEST Integration Pack - remove the SEST beta features. Quit Sea Power first.
rem Puts the normal SEST plugins back from the backups made when they were
rem installed and removes SEST's beta files. SETUP leaves them off until you
rem run "SEST beta features - turn on.cmd". Saves and data are kept.
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0sest-setup.ps1" -FromCmd -BetaFeatures Remove
if errorlevel 1 pause
