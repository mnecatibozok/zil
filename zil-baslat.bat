@echo off
title Zil Sistemi
cd /d "%~dp0"
set HTML_FILE=zil.html

:: HTML dosyasi kontrolu
if not exist "%HTML_FILE%" (
    for %%f in (zil-program*.html) do (
        set HTML_FILE=%%f
        echo [BILGI] zil.html bulunamadi, %%f kullaniliyor.
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

:: Python kontrolu
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

:: Eski Zil Chrome penceresini kapat
wmic process where "commandline like '%%ZilSistemi%%'" call terminate >nul 2>&1
timeout /t 1 /nobreak >nul

:: Eski port dosyasini temizle
if exist "zil-port.txt" del "zil-port.txt"

:: Firewall kurali
netsh advfirewall firewall add rule name="Zil Sistemi" dir=in action=allow protocol=TCP localport=8765-8800 >nul 2>&1

:: Sunucuyu gorulur konsol ile baslat
start "Zil Sunucu" /MIN %PYTHON_CMD% "%~dp0zunucu\sunucu.py"

:: Port dosyasinin olusmasini bekle (max 15 saniye)
set /a WAIT=0
:WAITLOOP
timeout /t 1 /nobreak >nul
set /a WAIT+=1
if exist "zil-port.txt" goto PORTFOUND
if %WAIT% GEQ 15 goto FALLBACK
goto WAITLOOP

:PORTFOUND
set /p ZIL_PORT=<zil-port.txt
echo [ZIL] Port: %ZIL_PORT%
set ZIL_URL=http://localhost:%ZIL_PORT%/%HTML_FILE%?fullscreen=1
goto LAUNCHBROWSER

:FALLBACK
echo [UYARI] Sunucu 15 saniyede baslamadi, 8765 portu deneniyor...
set ZIL_PORT=8765
set ZIL_URL=http://localhost:%ZIL_PORT%/%HTML_FILE%?fullscreen=1

:LAUNCHBROWSER

:: Chrome konumunu bul
set CHROME_EXE=
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe"      set CHROME_EXE=%ProgramFiles%\Google\Chrome\Application\chrome.exe
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set CHROME_EXE=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe
if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe"       set CHROME_EXE=%LocalAppData%\Google\Chrome\Application\chrome.exe

if "%CHROME_EXE%"=="" (
    start "" "%ZIL_URL%"
    goto END
)

:: Kiosk modu: tam ekran, on planda, gorev cubugu gizli
:: Cikiş icin: Alt+F4
:: NOT: --user-data-dir olmadan kiosk modu calismiyor, bu yuzden birakildi
start "" "%CHROME_EXE%" --kiosk "%ZIL_URL%" --user-data-dir="%TEMP%\ZilSistemi" --disable-session-crashed-bubble --disable-infobars --noerrdialogs --autoplay-policy=no-user-gesture-required --no-first-run --disable-translate

:: Chrome yuklenmesi icin bekle, sonra pencereyi on plana getir
timeout /t 3 /nobreak >nul
powershell -NoProfile -NonInteractive -WindowStyle Hidden -Command ^
  "$retries = 8;" ^
  "for ($i=0; $i -lt $retries; $i++) {" ^
  "  $wsh = New-Object -ComObject WScript.Shell;" ^
  "  $procs = Get-Process chrome -ErrorAction SilentlyContinue |" ^
  "    Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -ne '' };" ^
  "  if ($procs) {" ^
  "    Add-Type -AssemblyName Microsoft.VisualBasic;" ^
  "    Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class W { [DllImport(\"user32.dll\")] public static extern bool SetForegroundWindow(IntPtr h); [DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr h, int n); [DllImport(\"user32.dll\")] public static extern bool BringWindowToTop(IntPtr h); }';" ^
  "    foreach ($p in $procs) {" ^
  "      [W]::ShowWindow($p.MainWindowHandle, 9);" ^
  "      [W]::SetForegroundWindow($p.MainWindowHandle);" ^
  "      [W]::BringWindowToTop($p.MainWindowHandle);" ^
  "    };" ^
  "    break;" ^
  "  };" ^
  "  Start-Sleep -Milliseconds 1500;" ^
  "}"

:END
exit
