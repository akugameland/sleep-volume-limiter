@echo off
rem Ses Sinirlayici'yi konsol penceresi olmadan acar. Ilk acilista kurulumu kendisi yapar.
setlocal
rem Guvenlik: komutlari bu klasorde arama (klasore konmus sahte pythonw.exe calismasin)
set NoDefaultCurrentDirectoryInExePath=1
cd /d "%~dp0"
if exist ".venv\kurulum_tamam" goto baslat
call "%~dp0KURULUM.bat" otomatik
if not exist ".venv\kurulum_tamam" exit /b 1
:baslat
start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0ses_limiter.py"
