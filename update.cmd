@echo off
cd /d "%~dp0"
echo Page sizes are configured at the top of content.json:
echo   settings.publications_per_page
echo   settings.news_per_page
echo.
python update.py
pause
