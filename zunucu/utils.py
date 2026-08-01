#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zil Sistemi — Shared Utility Functions"""

import os, re, socket, struct, time
from datetime import datetime

SOUND_EXTENSIONS = ('.mp3', '.m4a', '.aac', '.ogg', '.wav', '.flac')


# ── Text processing ───────────────────────────────────────

def parse_first6(html: str) -> dict | None:
    """Extracts the first 6 ordered times from HTML as prayer times."""
    all_times = re.findall(r'>(\d{2}:\d{2})<', html)
    seen = []
    for t in all_times:
        if t not in seen:
            seen.append(t)
        if len(seen) >= 6:
            break
    if len(seen) >= 6:
        nums = [int(v.replace(':', '')) for v in seen[:6]]
        if nums == sorted(nums):
            keys = ['imsak', 'gunes', 'ogle', 'ikindi', 'aksam', 'yatsi']
            return dict(zip(keys, seen[:6]))
    return None


def slugify_tr(s: str) -> str:
    """Converts Turkish characters to ASCII, producing a URL-safe slug."""
    result = s.lower()
    for c_from, c_to in [
        ('\u0130', 'i'), ('\u015e', 's'), ('\u00c7', 'c'), ('\u00d6', 'o'),
        ('\u00dc', 'u'), ('\u011e', 'g'), ('\u0131', 'i'), ('\u015f', 's'),
        ('\u00e7', 'c'), ('\u00f6', 'o'), ('\u00fc', 'u'), ('\u011f', 'g'),
        (' ', '-'),
    ]:
        result = result.replace(c_from, c_to)
    return ''.join(ch for ch in result if ch in 'abcdefghijklmnopqrstuvwxyz0123456789-')


def ascii_upper_tr(s: str) -> str:
    """Converts Turkish characters to their uppercase ASCII equivalent (for dict key matching)."""
    result = s.upper()
    for c_from, c_to in [
        ('\u0130', 'I'), ('\u015e', 'S'), ('\u00c7', 'C'), ('\u00d6', 'O'),
        ('\u00dc', 'U'), ('\u011e', 'G'), ('\u0131', 'I'), ('\u015f', 'S'),
        ('\u00e7', 'C'), ('\u00f6', 'O'), ('\u00fc', 'U'), ('\u011f', 'G'),
    ]:
        result = result.replace(c_from, c_to)
    return result


# ── NTP Clock Check ───────────────────────────────────────

def ntp_offset_seconds(server: str = 'pool.ntp.org', timeout: int = 3) -> float | None:
    """
    Fetches real time from an NTP server and returns the offset from system
    clock in seconds. Positive: system clock is ahead; negative: behind.
    Returns None on connection failure or error.
    """
    try:
        # NTP packet — 48 bytes, LI=0 VN=3 Mode=3 (client)
        packet = bytearray(48)
        packet[0] = 0b00011011  # LI=0, VN=3, Mode=3
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)
            sent = time.time()
            s.sendto(bytes(packet), (server, 123))
            reply, _ = s.recvfrom(48)
        received = time.time()
        if len(reply) < 48:
            return None
        # NTP timestamp: seconds at bytes 40-43 (Transmit Timestamp)
        ntp_seconds = struct.unpack('!I', reply[40:44])[0]
        # NTP epoch: Jan 1 1900; Unix epoch: Jan 1 1970 → 70-year difference
        DELTA = 2208988800
        ntp_unix = ntp_seconds - DELTA
        # Split network delay in half
        delay = (received - sent) / 2
        offset = (sent + delay) - ntp_unix
        return round(offset, 2)
    except Exception:
        return None


def find_free_port(start: int = 8765, end: int = 8800) -> int:
    """Finds a free TCP port in the start–end range; falls back to OS-assigned random port."""
    for port in range(start, end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 0))
        return s.getsockname()[1]


# ── File manifests ────────────────────────────────────────

def build_manifest(base_dir: str) -> list:
    """Returns the list of sound files in the zilsesleri/ folder."""
    manifest = []
    d = os.path.join(base_dir, 'zilsesleri')
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.lower().endswith(SOUND_EXTENSIONS):
                manifest.append({'file': f, 'path': f'zilsesleri/{f}'})
    return manifest


def build_mp3_manifest(base_dir: str) -> dict:
    """Returns a folder→files dict for files in mp3/ subfolders."""
    result = {}
    d = os.path.join(base_dir, 'mp3')
    if not os.path.isdir(d):
        return result
    for folder in sorted(os.listdir(d)):
        fp = os.path.join(d, folder)
        if os.path.isdir(fp):
            files = [
                {'file': f, 'path': f'mp3/{folder}/{f}'}
                for f in sorted(os.listdir(fp))
                if f.lower().endswith(SOUND_EXTENSIONS)
            ]
            if files:
                result[folder] = files
    return result
