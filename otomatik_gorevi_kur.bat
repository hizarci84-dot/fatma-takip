@echo off
chcp 65001 > nul
cls
echo ====================================================================
echo  FATMA OZMIL - 1. ASAMA CALISMA PROGRAMI
echo  HER SABAH OTOMATIK WHATSAPP MESAJI KURULUMU (WINDOWS GOREV ZAMANLAYICI)
echo ====================================================================
echo.
echo Bu islem; 26 Eylul 2026 - 1 Mayis 2027 tarihleri arasinda
echo her sabah saat 08:00'da gunun programini Green API uzerinden
echo ogrencinin WhatsApp grubuna otomatik olarak gonderecektir.
echo.
python "%~dp0green_api_sender.py" --install-task 08:00
echo.
pause
