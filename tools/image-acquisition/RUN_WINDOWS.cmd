@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 fetch_images.py --mode all
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3.9+ is required. Install Python and run again.
    pause
    exit /b 1
  )
  python fetch_images.py --mode all
)
if errorlevel 1 (
  echo Image acquisition had an error; inspect the messages above.
  pause
  exit /b 1
)
if exist "CONTACT_SHEET.html" start "" "CONTACT_SHEET.html"
echo Finished. All new images are candidates until reviewed.
pause
