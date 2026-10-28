@echo off
setlocal
rem Guvenlik: komutlari bu klasorde arama (klasore konmus sahte python.exe calismasin)
set NoDefaultCurrentDirectoryInExePath=1
cd /d "%~dp0"
echo Ses Sinirlayici - kurulum
echo Python 3.12 ve 3 kucuk paket (pycaw, comtypes, psutil) bu klasordeki .venv icine kurulur.
echo.
set "PY="
if exist ".venv\kurulum_tamam" del ".venv\kurulum_tamam"

echo [1/3] Python 3.12
call :python_bul
if defined PY goto ortam

rem Python 3.12 yok: winget ile kullanici hesabina kur (yonetici izni gerekmez)
echo [UYARI] Python 3.12 bulunamadi, otomatik kuruluyor (birkac dakika)...
where winget >nul 2>nul || goto elle_kur
winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements
call :python_bul
if defined PY goto ortam

:elle_kur
echo.
echo [HATA] Python 3.12 otomatik kurulamadi. Lutfen elle kurun:
echo   https://www.python.org/downloads/release/python-31210/ - "Windows installer (64-bit)",
echo   ilk ekranda "Add python.exe to PATH" kutusunu isaretleyin, sonra KURULUM.bat'i yeniden calistirin.
pause
exit /b 1

:ortam
echo [TAMAM] Python: %PY%
echo [2/3] Python ortami (.venv)
"%PY%" -m venv --clear .venv
if errorlevel 1 goto hata

echo [3/3] Paketler (yalniz sabit surum ve dogrulanmis parmak iziyle)
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check --no-input --require-hashes --only-binary :all: --no-deps -r requirements.txt
if errorlevel 1 goto hata
".venv\Scripts\python.exe" -c "import tkinter, pycaw.pycaw" || goto hata

echo ok> ".venv\kurulum_tamam"
echo.
echo Kurulum tamam.
rem Baslat.bat cagirdiysa beklemeden programa gec
if /i "%~1"=="otomatik" exit /b 0
echo Programi Baslat.bat ile acin.
pause
exit /b 0

:hata
echo.
echo [HATA] Kurulum tamamlanamadi. Yukaridaki mesaja bakin ve KURULUM.bat'i yeniden calistirin.
echo        Internet baglantisi gerekir. Program aciksa once kapatin.
pause
exit /b 1

rem PY: bulunan Python 3.12. Yeni kurulan Python bu pencerenin PATH'inde henuz gorunmez,
rem bu yuzden once bilinen kurulum klasorlerine bakilir.
:python_bul
set "PY="
for %%P in ("%LOCALAPPDATA%\Programs\Python\Python312\python.exe" "%ProgramFiles%\Python312\python.exe") do (
  if not defined PY if exist %%P set "PY=%%~P"
)
if defined PY exit /b 0
for /f "delims=" %%P in ('py -3.12 -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%P"
if defined PY exit /b 0
rem Microsoft Store'un sahte python.exe'si bir sey yazmaz, yanlislikla secilmez
for /f "delims=" %%P in ('python -c "import sys; print(sys.executable if sys.version_info[:2] == (3, 12) else '')" 2^>nul') do set "PY=%%P"
exit /b 0
