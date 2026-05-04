#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zil Sistemi — Watchdog (zil handshake ve alarm sistemi)"""

import json, os, threading, time
from datetime import datetime

WATCHDOG_TIMEOUT = 10          # saniye — bu sürede handshake gelmezse alarm
LOG_FILE         = 'zil-alarm.log'
PROGRAM_FILE     = 'watchdog-program.json'


class ZilWatchdog:
    """
    İki görevi var:
      1. Her zil olayında HTML'den handshake bekler; 10 saniyede gelmezse alarm üretir.
      2. Günlük aktif zil listesini (A=1 olan ziller) program_guncelle() ile alır.
         Pause durumu bildirilir; pause'daki ziller için ATLANDI handshake'i de gelir.
    """

    def __init__(self):
        self._lock    = threading.Lock()
        self.beklenen : dict[str, float] = {}   # {key: bekleme_başlangıç_ts}
        self.program  : list[dict]       = []   # [{key, saat, tur}, ...]
        self.paused   : bool             = False
        self.alarmlar : list[dict]       = []   # Son alarmlar — /api/watchdog-durumu için

    # ── Dışarıdan çağrılan metotlar ──────────────────────

    def program_guncelle(self, zil_listesi: list, gun_idx: int | None = None) -> None:
        """HTML saveTimes() sonrasında çağrılır. Sadece A=1 olan zilleri alır."""
        with self._lock:
            self.program = zil_listesi
            # Artık programda olmayan key'leri bekleme listesinden çıkar
            yeni_keyler = {z['key'] for z in zil_listesi}
            eskiler = [k for k in self.beklenen if k not in yeni_keyler]
            for k in eskiler:
                del self.beklenen[k]
                print(f'[WD] Programdan çıkan key beklenmeyecek: {k}')
        # Program yedeklemesi
        try:
            with open(PROGRAM_FILE, 'w', encoding='utf-8') as f:
                json.dump(zil_listesi, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'[WD] Program yedek yazma hatası: {e}')

    def handshake_al(self, key: str, tip: str = 'CALINDI') -> None:
        """HTML'den gelen handshake. tip=CALINDI veya ATLANDI."""
        with self._lock:
            if key in self.beklenen:
                del self.beklenen[key]
                print(f'[WD] ✓ Handshake: {key} ({tip})')

    def pause_bildir(self, aktif: bool) -> None:
        """Pause başlayınca True, bitince False gönderilir."""
        with self._lock:
            self.paused = aktif
        print(f'[WD] Pause: {"DURAKLATILDI" if aktif else "DEVAM EDİYOR"}')

    def watchdog_durumu(self) -> dict:
        """HTML'in periyodik olarak yokladığı endpoint için veri döner."""
        with self._lock:
            simdi = time.time()
            son = [a for a in self.alarmlar if simdi - a['ts'] < 120]
            self.alarmlar = son
            return {
                'ok'            : True,
                'alarm'         : len(son) > 0,
                'alarmlar'      : son,
                'paused'        : self.paused,
                'beklenen_sayi' : len(self.beklenen),
            }

    # ── İç metotlar ──────────────────────────────────────

    def _program_oku_yedekten(self) -> None:
        """Sunucu yeniden başlarken program yedeğini okur."""
        try:
            if os.path.exists(PROGRAM_FILE):
                with open(PROGRAM_FILE, 'r', encoding='utf-8') as f:
                    self.program = json.load(f)
                print(f'[WD] Program yedeği yüklendi: {len(self.program)} zil')
        except Exception as e:
            print(f'[WD] Program yedeği okunamadı: {e}')

    def _alarm_uret(self, key: str) -> None:
        """Handshake gelmeyen zil için alarm üretir ve kaydeder."""
        simdi_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        mesaj = f'[ALARM] {simdi_str} — Handshake GELMEDI: {key}'
        print(mesaj)
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(mesaj + '\n')
        except Exception as e:
            print(f'[WD] Log yazma hatası: {e}')
        with self._lock:
            self.alarmlar.append({'key': key, 'zaman': simdi_str, 'ts': time.time()})
            self.beklenen.pop(key, None)

    def calistir(self) -> None:
        """Arka plan thread'i — her saniye çalışır."""
        self._program_oku_yedekten()
        print('[WD] Watchdog başladı.')
        _son_gun = datetime.now().date()

        while True:
            try:
                simdi  = datetime.now()
                ts     = f'{simdi.hour:02d}:{simdi.minute:02d}'
                bugun  = simdi.date()

                # Gün değiştiyse geçmiş bekleme ve alarmları temizle
                if bugun != _son_gun:
                    _son_gun = bugun
                    with self._lock:
                        self.beklenen.clear()
                        self.alarmlar.clear()
                    print('[WD] Yeni gün — beklenen ve alarm listesi temizlendi.')

                # Zil saati geldiyse bekleme listesine ekle
                if not self.paused:
                    bugun_idx     = simdi.weekday()          # 0=Pzt … 6=Paz
                    bugun_prefix  = f'd{bugun_idx}_'
                    with self._lock:
                        for zil in self.program:
                            key = zil.get('key', '')
                            if not key.startswith(bugun_prefix):
                                continue
                            if zil.get('saat') == ts and key not in self.beklenen:
                                self.beklenen[key] = time.time()

                # Timeout kontrolü
                with self._lock:
                    gecmisler = [
                        k for k, t in self.beklenen.items()
                        if time.time() - t > WATCHDOG_TIMEOUT
                    ]
                for key in gecmisler:
                    self._alarm_uret(key)

            except Exception as e:
                print(f'[WD] Döngü hatası: {e}')

            time.sleep(1)
