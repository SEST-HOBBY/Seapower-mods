@echo off
rem SEST Integration Pack - setup. Runs sest-setup.ps1 beside this file.
rem Quit Sea Power first. Safe to run again.
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0sest-setup.ps1" -FromCmd
if errorlevel 1 pause
