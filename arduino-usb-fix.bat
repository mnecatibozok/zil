@echo off
:: ============================================================
::  Arduino USB Baglanti Sorunu Giderici
::  Bir kez yonetici olarak calistirin — kalici olarak uygulanir
::  Zil Sistemi — Arduino Uno icin
:: ============================================================
title Arduino USB Fix

:: Yonetici yetkisi kontrolu
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Bu dosya YONETICI olarak calistirilmalidir.
    echo.
    echo     Uzerine sag tiklayin ^> "Yonetici olarak calistir"
    echo.
    pause
    exit /b 1
)

echo.
echo  ============================================================
echo   Arduino USB Baglanti Sorunu Giderici
echo   Zil Sistemi
echo  ============================================================
echo.

:: ── 1. USB Selective Suspend kapat ──────────────────────────
echo [1/4] USB Selective Suspend kapatiliyor...
powercfg /setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
powercfg /setdcvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
powercfg /apply
if %errorLevel% equ 0 (
    echo     [OK] USB Selective Suspend devre disi birakildi.
) else (
    echo     [!] Guec plani guncelleme basarisiz - devam ediliyor...
)

:: ── 2. Tum USB Root Hub'larin guc yonetimini kapat ──────────
echo [2/4] USB Hub guc yonetimi kapatiliyor...
powershell -NoProfile -NonInteractive -Command ^
  "Get-WmiObject -Namespace root\wmi -Class MSPower_DeviceEnable | Where-Object { $_.InstanceName -match 'USB' } | ForEach-Object { $_.Enable = $false; $_.Put() }" >nul 2>&1

:: Device Manager uzerinden USB Root Hub ayarlari (registry)
for /f "tokens=*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Enum\USB" /s /f "DeviceDesc" 2^>nul ^| findstr /i "root hub"') do (
    reg add "%%a" /v "EnhancedPowerManagementEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
)
echo     [OK] USB Hub guc yonetimi kapatildi.

:: ── 3. Arduino COM port sabit numaraya atama rehberi ────────
echo [3/4] Arduino COM port bilgisi aliniyor...
echo.
echo     Mevcut COM portlari:
wmic path Win32_PnPEntity where "Name like '%%COM%%'" get Name,DeviceID 2>nul | findstr /i "arduino\|ch340\|ch341\|atmega\|serial\|usb"
if %errorLevel% neq 0 (
    echo     Arduino simdi takili degil veya surucu sorunu var.
)
echo.
echo     NOT: Arduino her takildiginda COM numarasi degisiyorsa
echo     Device Manager ^> Ports ^> Arduino ^> Ozellikler ^>
echo     Port Ayarlari ^> Gelismis ^> COM Port Numarasi
echo     bolumund en sabit bir numara seciniz ^(orn: COM3^).
echo.

:: ── 4. Windows USB numaralandirma servisini yenile ──────────
echo [4/4] USB numaralandirma servisi yenileniyor...
net stop "Device Install Service" >nul 2>&1
net start "Device Install Service" >nul 2>&1
echo     [OK] Servis yenilendi.

:: ── Sonuc ────────────────────────────────────────────────────
echo.
echo  ============================================================
echo   Tamamlandi!
echo.
echo   Yapilan islemler:
echo   - USB Selective Suspend: KAPALI (Windows USB'yi artik uyutmaz)
echo   - USB Hub guc yonetimi: KAPALI
echo   - USB numaralandirma servisi yenilendi
echo.
echo   Onerilen sonraki adimlar:
echo   1. Arduino'yu cikarin ve yeniden takin
echo   2. Zil programini baslatin
echo   3. Sorun tekrarlarsa bilgisayari yeniden baslatiniz
echo  ============================================================
echo.
pause
