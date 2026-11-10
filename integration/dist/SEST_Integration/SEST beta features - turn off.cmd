@echo off
rem SEST Integration Pack - turn the SEST beta features off. Quit Sea Power first.
rem Their loader stays installed but inactive, and SETUP leaves it off until
rem you run "SEST beta features - turn on.cmd". Nothing else is changed.
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0sest-setup.ps1" -FromCmd -BetaFeatures Off
if errorlevel 1 pause
