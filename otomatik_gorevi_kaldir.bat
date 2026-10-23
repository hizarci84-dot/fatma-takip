@echo off
chcp 65001 > nul
cls
echo ====================================================================
echo  FATMA OZMIL - 1. ASAMA CALISMA PROGRAMI
echo  OTOMATIK GOREVI KALDIR
echo ====================================================================
echo.
python "%~dp0green_api_sender.py" --uninstall-task
echo.
pause
