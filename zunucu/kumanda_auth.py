#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zil Sistemi — /kumanda (uzaktan kumanda) sayfası için PIN korumalı oturum yönetimi.

Ağdaki HERKES /kumanda sayfasına erişebiliyordu (parola yoktu). Bu modül basit
bir PIN + oturum çerezi katmanı ekler: doğru PIN girilmeden ne kumanda
butonları görünür, ne de /api/remote komutu kabul edilir.
"""

import json, os, secrets, time

PIN_FILE     = 'kumanda-pin.json'
SESSION_TTL  = 24 * 60 * 60  # Oturum çerezi 24 saat geçerli
COOKIE_NAME  = 'zil_kumanda_session'

# Aktif oturum token'ları — bellekte tutulur (sunucu yeniden başlayınca sıfırlanır)
_sessions: dict[str, float] = {}


def _pin_path() -> str:
    return os.path.join(os.getcwd(), PIN_FILE)


def get_or_create_pin() -> str:
    """PIN dosyasını okur; yoksa rastgele 6 haneli bir PIN üretip kaydeder."""
    try:
        with open(_pin_path(), 'r', encoding='utf-8') as f:
            data = json.load(f)
            pin = str(data.get('pin', '')).strip()
            if pin:
                return pin
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    pin = f'{secrets.randbelow(1_000_000):06d}'
    try:
        with open(_pin_path(), 'w', encoding='utf-8') as f:
            json.dump({'pin': pin}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return pin


def verify_pin(candidate: str) -> bool:
    return isinstance(candidate, str) and candidate.strip() == get_or_create_pin()


def create_session() -> str:
    token = secrets.token_hex(16)
    _sessions[token] = time.time() + SESSION_TTL
    _cleanup()
    return token


def is_valid_session(token: str | None) -> bool:
    if not token:
        return False
    exp = _sessions.get(token)
    if exp is None:
        return False
    if time.time() > exp:
        _sessions.pop(token, None)
        return False
    return True


def _cleanup() -> None:
    now = time.time()
    for tok in [t for t, exp in _sessions.items() if exp < now]:
        _sessions.pop(tok, None)


def parse_cookie(cookie_header: str | None) -> str | None:
    """Cookie header'ından oturum token'ını çıkarır (üçüncü taraf kütüphane kullanmadan)."""
    if not cookie_header:
        return None
    for part in cookie_header.split(';'):
        part = part.strip()
        if part.startswith(COOKIE_NAME + '='):
            return part[len(COOKIE_NAME) + 1:]
    return None
