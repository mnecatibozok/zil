#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zil Sistemi — Anons Ayarları (zilsesleri/ dosyaları)"""

import json, os

AYAR_DOSYA  = 'zil-anons-ayar.json'

# ── Zil Ses Ayarları ─────────────────────────────────────
ZIL_SES_AYAR_DOSYA = 'zil-ses-ayar.json'

# Hangi SND_DEFS anahtarı için hangi dosya adı kullanılacak.
# Boş string = SND_DEFS'teki varsayılan dosyayı kullan.
ZIL_SES_VARSAYILAN = {
    'zil'          : '',
    'zilTenefus'   : '',
    'zilOgrenci'   : '',
    'zilOgretmen'  : '',
    'zilToplanma'  : '',
    'mars'         : '',
    'saygi'        : '',
    'saygi2dk'     : '',
    'depremIkaz'   : '',
    'depremTahliye': '',
}


def _zil_ses_yolu() -> str:
    return os.path.join(os.getcwd(), ZIL_SES_AYAR_DOSYA)


def load_zil_ses_ayar() -> dict:
    """Zil ses ayarlarını JSON dosyasından okur. Dosya yoksa boş varsayılanları döner."""
    try:
        with open(_zil_ses_yolu(), 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {k: str(data.get(k, '')).strip() for k in ZIL_SES_VARSAYILAN}
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(ZIL_SES_VARSAYILAN)


def save_zil_ses_ayar(ayar: dict) -> dict:
    """Zil ses ayarlarını JSON dosyasına yazar. Geçerli anahtarları filtreler."""
    data = {k: str(ayar.get(k, '')).strip() for k in ZIL_SES_VARSAYILAN}
    with open(_zil_ses_yolu(), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data

# Varsayılan: tüm zil tipleri için anons yok
VARSAYILAN = {
    'ogretmen' : 'anons_ogretmen.mp3',   # Öğretmen zili (ilk ders dahil) sonrası anons
    'ogrenci'  : 'anons_ogrenci.mp3',    # Öğrenci zili sonrası anons
    'toplanma' : 'anons_toplanma.mp3',   # Toplanma zili sonrası anons
    'sonZil'   : 'anons_gunsonu.mp3',    # Son zil (gün sonu) sonrası anons
    'tenefus'  : 'anons_tenefus.mp3',    # Tenefüs çıkışı (ders bitti) sonrası anons
}


def _dosya_yolu() -> str:
    return os.path.join(os.getcwd(), AYAR_DOSYA)


def load_anons_ayar() -> dict:
    """JSON dosyasından anons ayarlarını okur. Dosya yoksa varsayılanları döner."""
    try:
        with open(_dosya_yolu(), 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Eksik anahtarları varsayılanla tamamla
        return {**VARSAYILAN, **{k: data.get(k, '') for k in VARSAYILAN}}
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(VARSAYILAN)


def save_anons_ayar(ayar: dict) -> dict:
    """Anons ayarlarını JSON dosyasına yazar. Geçerli anahtarları filtreler."""
    data = {k: str(ayar.get(k, '')).strip() for k in VARSAYILAN}
    with open(_dosya_yolu(), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data
