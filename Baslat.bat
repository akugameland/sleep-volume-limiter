@echo off
rem Ses Sinirlayici'yi konsol penceresi olmadan acar.
cd /d "%~dp0"
start "" pythonw "%~dp0ses_limiter.py"
