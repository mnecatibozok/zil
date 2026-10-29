#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zil Sistemi — Bell/Announcement Sound Settings (zilsesleri/ files)"""

import json, os

from utils import atomic_write_json

CONFIG_FILE = 'bell-announcement-config.json'

# ── Bell Sound Settings ──────────────────────────────────
BELL_SOUND_CONFIG_FILE = 'bell-sound-config.json'

# Which filename to use for each SND_DEFS key.
# Empty string = use the default file defined in SND_DEFS.
BELL_SOUND_DEFAULTS = {
    'bell'          : '',
    'bellBreak'     : '',
    'bellStudent'   : '',
    'bellTeacher'   : '',
    'bellAssembly'  : '',
    'anthem'        : '',
    'tribute'       : '',
    'tribute2min'   : '',
    'alarmAlert'    : '',
    'alarmEvacuate' : '',
}


def _bell_sound_path() -> str:
    return os.path.join(os.getcwd(), BELL_SOUND_CONFIG_FILE)


def load_bell_sound_config() -> dict:
    """Reads bell sound settings from the JSON file. Returns empty defaults if missing."""
    try:
        with open(_bell_sound_path(), 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {k: str(data.get(k, '')).strip() for k in BELL_SOUND_DEFAULTS}
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(BELL_SOUND_DEFAULTS)


def save_bell_sound_config(config: dict) -> dict:
    """Writes bell sound settings to the JSON file. Filters to valid keys only."""
    data = {k: str(config.get(k, '')).strip() for k in BELL_SOUND_DEFAULTS}
    atomic_write_json(_bell_sound_path(), data, indent=2)
    return data

# Varsayılan anons dosyaları (break: dosya olmadığı için boş = tenefüste anons yok)
DEFAULTS = {
    'teacher' : 'anons_ogretmen.mp3',   # Announcement after teacher bell (incl. first period)
    'student' : 'anons_ogrenci.mp3',    # Announcement after student bell
    'assembly': 'anons_toplanma.mp3',   # Announcement after assembly bell
    'lastBell': 'anons_gunsonu.mp3',    # Announcement after last bell (end of day)
    'break'   : '',    # Announcement after break (period end)
}


def _config_path() -> str:
    return os.path.join(os.getcwd(), CONFIG_FILE)


def load_announcement_config() -> dict:
    """Reads announcement settings from the JSON file. Returns defaults if missing."""
    try:
        with open(_config_path(), 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Dosyada olmayan anahtar boş kalır (anons yok)
        return {k: str(data.get(k, '')).strip() for k in DEFAULTS}
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULTS)


def save_announcement_config(config: dict) -> dict:
    """Writes announcement settings to the JSON file. Filters to valid keys only."""
    data = {k: str(config.get(k, '')).strip() for k in DEFAULTS}
    atomic_write_json(_config_path(), data, indent=2)
    return data
