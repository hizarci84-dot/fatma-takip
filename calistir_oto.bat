@echo off
chcp 65001 > nul
cd /d "%~dp0"
python green_api_sender.py --auto >> gunluk_gonderim_gunlugu.log 2>&1
