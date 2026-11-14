#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zil Sistemi — Kalıcı Ayar Yedeği (localStorage için sunucu tarafı yedek)

Tarayıcı localStorage'ı tarayıcı profiline bağlıdır. Kiosk Chrome profili
artık program klasöründeki chrome-profil/ içinde tutulur; yine de bir
"oturum sıfırlama"/temizlik yazılımı veya elle silme profili yok ederse
localStorage'daki ayarlar kaybolabilir. Bu modül tüm zil* ayarlarını (program, planlar, takvimler, sessiz mod, ezan, anfi vb.)
diskte ikinci kopya olarak tutar ve günde bir kez yedek/ klasörüne kopyalar.

Bu modül, seçili (whitelist'teki) localStorage anahtarlarını sunucu
diskindeki tek bir JSON dosyasına (zil-ayarlar.json) da eşler. Program her
açılışında önce bu dosya okunur ve localStorage'a geri yazılır (bkz.
zil.html → init() → _serverLoadSettingsIntoLocalStorage()); böylece
tarayıcı profili tamamen silinmiş olsa bile en son kaydedilen ayarlar
geri gelir.

Dosya doğrudan çift tıklanarak (sunucu olmadan file:// ile) açılırsa bu
uç noktalara erişilemez — bu durumda sistem sessizce yalnızca
localStorage ile çalışmaya devam eder (zil.html tarafında try/catch ile
korunuyor).
"""

import json, os, threading

SETTINGS_FILE = 'zil-ayarlar.json'
_lock = threading.Lock()

# Sunucuda yedeklenecek anahtarlar: "zil" önekli tüm localStorage anahtarları.
# Hacimli/geçici olanlar yedeklenmez.
SKIP_KEYS = {'zilCalmaGecmisi', 'zilMp3ZilQueue'}
BACKUP_DIR = 'yedek'      # günlük kopyalar buraya yazılır
BACKUP_KEEP = 14          # saklanacak gün sayısı


def is_allowed_key(key: str) -> bool:
    """Anahtarın sunucu yedeğine yazılmasına izin verilip verilmediğini döndürür."""
    return isinstance(key, str) and key.startswith('zil') and len(key) <= 64 and key not in SKIP_KEYS


def _daily_backup() -> None:
    """Ayar dosyasının günde bir kopyasını yedek/ klasörüne alır; eskileri siler."""
    try:
        import shutil, time, glob
        os.makedirs(BACKUP_DIR, exist_ok=True)
        dst = os.path.join(BACKUP_DIR, f"zil-ayarlar-{time.strftime('%Y-%m-%d')}.json")
        # Günde BİR kez: her kayıtta üzerine yazılırsa o günün yedeği hep "şu anki hâl" olur ve
        # hatalı bir değişiklikten geri dönülemezdi. Bugünün yedeği varsa dokunma.
        if os.path.exists(dst):
            return
        shutil.copyfile(_settings_path(), dst)
        for old in sorted(glob.glob(os.path.join(BACKUP_DIR, 'zil-ayarlar-*.json')))[:-BACKUP_KEEP]:
            os.remove(old)
    except Exception as e:
        print(f'[ZIL] Günlük yedek alınamadı: {e}')


def _settings_path() -> str:
    return os.path.join(os.getcwd(), SETTINGS_FILE)


def load_all_settings() -> dict:
    """Diskteki yedek dosyayı okur. Dosya yoksa/bozuksa boş dict döner."""
    try:
        with open(_settings_path(), 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _recover_corrupt()


def _recover_corrupt() -> dict:
    """Ayar dosyası bozulmuşsa (ör. elektrik kesintisi) bozuk dosyayı kenara alır ve en yeni günlük
    yedekten geri yükler. Aksi halde bir sonraki kayıt dosyayı tek anahtarla ezip TÜM ayarları kaybettirirdi."""
    try:
        import glob, time
        bad = _settings_path() + '.bozuk-' + time.strftime('%Y%m%d-%H%M%S')
        os.replace(_settings_path(), bad)
        print(f'[ZIL] Ayar dosyası bozuk — kenara alındı: {os.path.basename(bad)}')
        for f in sorted(glob.glob(os.path.join(BACKUP_DIR, 'zil-ayarlar-*.json')), reverse=True):
            try:
                with open(f, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                if isinstance(data, dict):
                    shutil_copy(f, _settings_path())
                    print(f'[ZIL] Ayarlar yedekten geri yüklendi: {os.path.basename(f)}')
                    return data
            except Exception:
                continue
    except Exception as e:
        print(f'[ZIL] Bozuk ayar dosyası kurtarılamadı: {e}')
    return {}


def shutil_copy(src, dst):
    import shutil
    shutil.copyfile(src, dst)


def save_one_setting(key: str, value) -> dict:
    """Tek bir anahtarı diskteki yedek dosyaya yazar (varsa günceller).

    Eş zamanlı POST istekleri (ör. birden fazla ayar art arda kaydedilirse)
    birbirini ezmesin diye dosya okuma+yazma bir kilit (_lock) altında yapılır.
    """
    if not is_allowed_key(key):
        raise ValueError(f'Yedeklenmesine izin verilmeyen anahtar: {key}')
    with _lock:
        data = load_all_settings()
        data[key] = value
        tmp_path = _settings_path() + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, _settings_path())  # atomik yer değiştirme — yarım yazılmış dosya riski yok
        _daily_backup()
    return data
