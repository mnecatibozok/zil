#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zil Sistemi — Tarayıcı bekçisi (watchdog).

Zil sayfası her ~5 sn'de /api/heartbeat çağırır. Sayfa bir kez canlı olduktan sonra
heartbeat STALE_SEC saniyeden uzun kesilirse (Chrome çöktü/donduysa) kiosk Chrome
yeniden başlatılır. /api/exit ve /api/shutdown bekçiyi devre dışı bırakır.
Kapatmak için ortam değişkeni: ZIL_WATCHDOG=0
"""
import os, shutil, subprocess, threading, time

STALE_SEC = 90           # bu kadar süre heartbeat gelmezse sayfa ölü sayılır
CHECK_SEC = 15           # kontrol aralığı
MIN_GAP_SEC = 120        # iki yeniden başlatma arası en az süre
MAX_PER_HOUR = 5         # döngüye girmeyi önlemek için saatlik üst sınır

_last_beat = 0.0
_enabled = os.environ.get('ZIL_WATCHDOG', '1') != '0'
_restarts: list[float] = []

# Chrome'un arka planda/örtülüyken zamanlayıcıları yavaşlatmasını engelleyen bayraklar (zil-baslat.bat ile aynı)
CHROME_FLAGS = ['--kiosk', '--disable-session-crashed-bubble', '--disable-infobars', '--noerrdialogs',
                '--autoplay-policy=no-user-gesture-required', '--no-first-run', '--disable-translate',
                '--disable-background-timer-throttling', '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows', '--disable-features=CalculateNativeWinOcclusion']


def beat() -> None:
    """Sayfadan gelen heartbeat'i kaydeder."""
    global _last_beat
    _last_beat = time.time()


def disable() -> None:
    """Bilinçli kapatma sırasında bekçinin Chrome'u geri açmasını engeller."""
    global _enabled
    _enabled = False


def _chrome_path() -> str | None:
    """Chrome/Chromium yürütülebilir dosyasını bulur."""
    if os.name == 'nt':
        for base in (os.environ.get('ProgramFiles'), os.environ.get('ProgramFiles(x86)'), os.environ.get('LocalAppData')):
            if base:
                p = os.path.join(base, 'Google', 'Chrome', 'Application', 'chrome.exe')
                if os.path.exists(p):
                    return p
        return None
    for name in ('chromium-browser', 'chromium', 'google-chrome', 'google-chrome-stable'):
        p = shutil.which(name)
        if p:
            return p
    return None


def _relaunch(url: str) -> None:
    """Eski kiosk Chrome'u kapatıp aynı profil ile yeniden açar."""
    exe = _chrome_path()
    if not exe:
        print('[WATCHDOG] Chrome bulunamadı — yeniden başlatılamadı.')
        return
    from handler import _close_kiosk_chrome
    _close_kiosk_chrome()
    time.sleep(1.5)
    profile = os.path.join(os.path.abspath(os.getcwd()), 'chrome-profil')
    subprocess.Popen([exe, *CHROME_FLAGS, url, f'--user-data-dir={profile}'])
    print('[WATCHDOG] Heartbeat kesildi — Chrome yeniden başlatıldı.')


def _loop(url: str) -> None:
    """Heartbeat'i izler; gerekirse Chrome'u yeniden başlatır."""
    global _last_beat
    while True:
        time.sleep(CHECK_SEC)
        if not _enabled or _last_beat == 0.0 or time.time() - _last_beat < STALE_SEC:
            continue
        now = time.time()
        _restarts[:] = [t for t in _restarts if now - t < 3600]
        if len(_restarts) >= MAX_PER_HOUR or (_restarts and now - _restarts[-1] < MIN_GAP_SEC):
            continue
        _restarts.append(now)
        _last_beat = now  # yeni sayfaya yüklenmesi için süre tanı
        try:
            _relaunch(url)
        except Exception as e:
            print(f'[WATCHDOG] Hata: {e}')


def start(port: int, html_file: str) -> None:
    """Bekçi iş parçacığını başlatır."""
    if not _enabled:
        print('[WATCHDOG] Devre dışı (ZIL_WATCHDOG=0).')
        return
    threading.Thread(target=_loop, args=(f'http://localhost:{port}/{html_file}?fullscreen=1',), daemon=True).start()
