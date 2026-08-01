#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zil Sistemi — Kalıcı Ayar Yedeği (localStorage için sunucu tarafı yedek)

Tarayıcı localStorage'ı tarayıcı profiline bağlıdır. Kiosk modunda Chrome
profili TEMP klasöründe tutulursa (veya bir "oturum sıfırlama"/temizlik
yazılımı profili silerse) localStorage'daki TÜM ayarlar (haftalık zil
programı, hafta sonu zil tikleri, tablo göster/gizle tercihi, okul bilgisi,
aktif plan vb.) kaybolur ve program her açılışta varsayılana dönüyormuş
gibi görünür.

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

# Sunucuda yedeklenecek localStorage anahtarları — güvenlik ve dosya
# boyutu için whitelist ile sınırlı tutuluyor. Kozmetik/önemsiz tercihler
# (ör. panel pin durumları, ses seviyesi) burada yok; istenirse eklenebilir.
ALLOWED_KEYS = {
    'zilSistemiV10',    # Haftalık gün ayarları + satır durumları + hafta sonu zil tikleri
    'zilAccordionView', # Ana sayfa "Tablo Göster/Gizle" switch'i
    'zilOkulBilgi',     # Okul adı / il-ilçe
    'zilAktivPlan',     # Aktif zil planı ('A' | 'B' | 'C')
}


def _settings_path() -> str:
    return os.path.join(os.getcwd(), SETTINGS_FILE)


def load_all_settings() -> dict:
    """Diskteki yedek dosyayı okur. Dosya yoksa/bozuksa boş dict döner."""
    try:
        with open(_settings_path(), 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_one_setting(key: str, value) -> dict:
    """Tek bir anahtarı diskteki yedek dosyaya yazar (varsa günceller).

    Eş zamanlı POST istekleri (ör. birden fazla ayar art arda kaydedilirse)
    birbirini ezmesin diye dosya okuma+yazma bir kilit (_lock) altında yapılır.
    """
    if key not in ALLOWED_KEYS:
        raise ValueError(f'Yedeklenmesine izin verilmeyen anahtar: {key}')
    with _lock:
        data = load_all_settings()
        data[key] = value
        tmp_path = _settings_path() + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, _settings_path())  # atomik yer değiştirme — yarım yazılmış dosya riski yok
    return data
