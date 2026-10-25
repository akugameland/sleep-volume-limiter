@echo off
rem Ses Sinirlayici'yi konsol penceresi olmadan acar.
setlocal
rem Guvenlik: komutlari bu klasorde arama (klasore konmus sahte pythonw.exe calismasin)
set NoDefaultCurrentDirectoryInExePath=1
cd /d "%~dp0"
start "" pythonw "%~dp0ses_limiter.py"
