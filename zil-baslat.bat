@echo off
title Zil Sistemi v1
cd /d "%~dp0"
set HTML_FILE=zil-programi-v1.html

:: HTML dosyasi kontrolu
if not exist "%HTML_FILE%" (
    for %%f in (zil-program*.html) do (
        set HTML_FILE=%%f
        echo [BILGI] zil-programi-v1.html bulunamadi, %%f kullaniliyor.
        goto :HTML_FOUND
    )
    echo [HATA] HTML dosyasi bulunamadi!
    pause & exit /b 1
)
:HTML_FOUND

:: Sunucu dosyasi kontrolu
if not exist "zunucu\sunucu.py" (
    echo [HATA] zunucu\sunucu.py bulunamadi!
    pause & exit /b 1
)

:: Python kontrolu — python oncelikli (konsol gorsunsun)
set PYTHON_CMD=
where python >nul 2>&1 && set PYTHON_CMD=python
if "%PYTHON_CMD%"=="" (
    where py >nul 2>&1 && set PYTHON_CMD=py
)
if "%PYTHON_CMD%"=="" (
    where pythonw >nul 2>&1 && set PYTHON_CMD=pythonw
)
if "%PYTHON_CMD%"=="" (
    echo [HATA] Python kurulu degil!
    pause & exit /b 1
)

:: Eski sunucuyu oldur
taskkill /f /fi "WINDOWTITLE eq Zil Sunucu" >nul 2>&1
wmic process where "commandline like '%%sunucu.py%%'" call terminate >nul 2>&1
timeout /t 1 /nobreak >nul

:: Eski Zil Chrome penceresini kapat (sadece ZilSistemi profili — diger Chrome etkilenmez)
wmic process where "commandline like '%%ZilSistemi%%'" call terminate >nul 2>&1
timeout /t 1 /nobreak >nul

:: Eski port dosyasini temizle
if exist "zil-port.txt" del "zil-port.txt"

:: Firewall kurali
netsh advfirewall firewall add rule name="Zil Sistemi" dir=in action=allow protocol=TCP localport=8765-8800 >nul 2>&1

:: Sunucuyu gorulur konsol ile baslat (sunucu/ klasoründen)
start "Zil Sunucu" /MIN %PYTHON_CMD% "%~dp0zunucu\sunucu.py"

:: Port dosyasinin olusmasini bekle (max 10 saniye)
set /a WAIT=0
:WAITLOOP
timeout /t 1 /nobreak >nul
set /a WAIT+=1
if exist "zil-port.txt" goto PORTFOUND
if %WAIT% GEQ 10 goto FALLBACK
goto WAITLOOP

:PORTFOUND
set /p ZIL_PORT=<zil-port.txt
echo [ZIL] Port: %ZIL_PORT%

:: --app modu: sekme/adres cubugu yok, tam ekran, window.close() calisir (kiosk modunun aksine)
:: --user-data-dir: Zil programi icin izole Chrome profili — diger Chrome pencereleri etkilenmez
set CHROME_FLAGS=--user-data-dir="%TEMP%\ZilSistemi" --start-fullscreen --disable-session-crashed-bubble --disable-infobars --noerrdialogs

if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" --app="http://localhost:%ZIL_PORT%/%HTML_FILE%?fullscreen=1" %CHROME_FLAGS%
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" --app="http://localhost:%ZIL_PORT%/%HTML_FILE%?fullscreen=1" %CHROME_FLAGS%
) else if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" (
    start "" "%LocalAppData%\Google\Chrome\Application\chrome.exe" --app="http://localhost:%ZIL_PORT%/%HTML_FILE%?fullscreen=1" %CHROME_FLAGS%
) else (
    start "" "http://localhost:%ZIL_PORT%/%HTML_FILE%?fullscreen=1"
)
goto END

:FALLBACK
echo [UYARI] Sunucu 10 saniyede baslamadi, 8765 portu deneniyor...
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" --app="http://localhost:8765/%HTML_FILE%?fullscreen=1" %CHROME_FLAGS%
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" --app="http://localhost:8765/%HTML_FILE%?fullscreen=1" %CHROME_FLAGS%
) else if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" (
    start "" "%LocalAppData%\Google\Chrome\Application\chrome.exe" --app="http://localhost:8765/%HTML_FILE%?fullscreen=1" %CHROME_FLAGS%
) else (
    start "" "http://localhost:8765/%HTML_FILE%?fullscreen=1"
)

:END
exit
