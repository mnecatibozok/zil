#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zil Sistemi — Anons Ayarları (zilsesleri/ dosyaları)"""

import json, os

AYAR_DOSYA  = 'zil-anons-ayar.json'

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
