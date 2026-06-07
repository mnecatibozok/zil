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

:: Chrome'u DOGRUDAN bat'tan baslat (onceki calisma sekli - guvenilir)
start "" "%CHROME_EXE%" --app="%ZIL_URL%" --user-data-dir="%TEMP%\ZilSistemi" --start-fullscreen --disable-session-crashed-bubble --disable-infobars --noerrdialogs --autoplay-policy=no-user-gesture-required

:: On plana getirme: Chrome acilana kadar bekle, sonra focus ver
:: Gecici ps1 OLMADAN - dogrudan satir ici PowerShell kullan
powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -Command ^
  "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class W { [DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr h,int n); [DllImport(\"user32.dll\")] public static extern bool SetForegroundWindow(IntPtr h); [DllImport(\"user32.dll\")] public static extern bool BringWindowToTop(IntPtr h); [DllImport(\"user32.dll\")] public static extern IntPtr GetForegroundWindow(); [DllImport(\"user32.dll\")] public static extern uint GetWindowThreadProcessId(IntPtr h,out uint p); [DllImport(\"user32.dll\")] public static extern bool AttachThreadInput(uint a,uint b,bool c); [DllImport(\"kernel32.dll\")] public static extern uint GetCurrentThreadId(); }' -ErrorAction SilentlyContinue; $hw=[IntPtr]::Zero; for($i=0;$i -lt 20;$i++){Start-Sleep -Milliseconds 500; $p=Get-Process chrome -ErrorAction SilentlyContinue | Where-Object{$_.MainWindowHandle -ne 0} | Sort-Object StartTime -Descending; if($p){$hw=$p[0].MainWindowHandle;break}}; if($hw -ne [IntPtr]::Zero){for($j=0;$j -lt 3;$j++){[W]::ShowWindow($hw,9)|Out-Null;$fg=[W]::GetForegroundWindow();$ft=[W]::GetWindowThreadProcessId($fg,[ref][uint32]0);$mt=[W]::GetCurrentThreadId();[W]::AttachThreadInput($mt,$ft,$true)|Out-Null;[W]::BringWindowToTop($hw)|Out-Null;[W]::SetForegroundWindow($hw)|Out-Null;[W]::AttachThreadInput($mt,$ft,$false)|Out-Null;Start-Sleep -Milliseconds 400}}"

:END
exit
