@echo off
cd /d "%~dp0"
echo Update the website and publish to GitHub Pages
echo.
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.10 or later and try again.
  pause
  exit /b 1
)
python publish.py
set "publish_exit=%errorlevel%"
echo.
if not "%publish_exit%"=="0" echo Publishing failed. Read the message above.
pause
exit /b %publish_exit%
