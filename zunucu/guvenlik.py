#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zil Sistemi — Güvenlik yardımcıları.

* Hangi dosyaların tarayıcıya sunulabileceği (allowlist) — PIN, ayar, günlük, kaynak kod dosyaları ASLA sunulmaz
* İstemcinin "güvenilir" olup olmadığı (bu bilgisayar = loopback, ya da PIN ile giriş yapmış oturum)
* Host / Origin doğrulaması (CSRF ve DNS-rebinding koruması)
* PIN denemelerinde IP başına hız sınırı (kaba kuvvet koruması)
"""

import ipaddress, posixpath, re, socket, threading, time

SOUND_EXTENSIONS = ('.mp3', '.m4a', '.aac', '.ogg', '.wav', '.flac')

# ── 1) Statik dosya allowlist ────────────────────────────

_RE_ROOT   = re.compile(r'^/(zil[A-Za-z0-9_.\-]*\.html|twemoji\.min\.js)$')
_RE_SVG    = re.compile(r'^/svg/[A-Za-z0-9\-]+\.svg$')
_RE_LOCALE = re.compile(r'^/locales/[A-Za-z0-9\-]+\.json$')
_RE_AUDIO  = re.compile(r'^/(zilsesleri|mp3)/.+')


def static_allowed(url_path: str) -> bool:
    """Yalnızca arayüzün gerçekten ihtiyaç duyduğu dosyalara izin verir."""
    p = url_path or ''
    if '\x00' in p or '\\' in p or ':' in p:           # NUL, Windows ayırıcı ve ADS (dosya::$DATA) hileleri
        return False
    if posixpath.normpath(p) != p:                     # '..', '//', './' içeren yollar
        return False
    if _RE_ROOT.match(p) or _RE_SVG.match(p) or _RE_LOCALE.match(p):
        return True
    if _RE_AUDIO.match(p) and p.lower().endswith(SOUND_EXTENSIONS):
        return True
    return False


def audio_path_ok(rel_path: str) -> bool:
    """move-to-temp / restore için: yalnızca zilsesleri/ veya mp3/ altındaki ses dosyaları."""
    p = '/' + (rel_path or '').replace('\\', '/').lstrip('/')
    return bool(_RE_AUDIO.match(p)) and p.lower().endswith(SOUND_EXTENSIONS) and '..' not in p.split('/')


# ── 2) Güvenilir istemci ─────────────────────────────────

def is_loopback(addr: str) -> bool:
    try:
        ip = ipaddress.ip_address(addr.split('%')[0])
        if getattr(ip, 'ipv4_mapped', None):
            ip = ip.ipv4_mapped
        return ip.is_loopback
    except ValueError:
        return False


# ── 3) Host / Origin doğrulaması ─────────────────────────

def _host_only(hostport: str) -> str:
    h = (hostport or '').strip().lower()
    if h.startswith('['):                              # [::1]:8765
        return h[1:h.find(']')] if ']' in h else h
    return h.rsplit(':', 1)[0] if h.count(':') == 1 else h


_OWN_NAMES = set()
try:
    _hn = socket.gethostname().lower()
    _OWN_NAMES.update({_hn, _hn + '.local', 'localhost'})
except Exception:
    _OWN_NAMES.add('localhost')


def host_ok(host_header: str | None) -> bool:
    """IP adresi, localhost veya bu bilgisayarın adı kabul edilir. Başka bir alan adı
    (DNS rebinding: evil.example → 192.168.x.x) reddedilir."""
    if not host_header:
        return False
    h = _host_only(host_header)
    if h in _OWN_NAMES:
        return True
    try:
        ipaddress.ip_address(h)
        return True
    except ValueError:
        return False


def origin_ok(origin: str | None, host_header: str | None) -> bool:
    """POST isteğinde Origin varsa sunucunun kendi adresiyle aynı olmalı (başka siteden CSRF engellenir)."""
    if not origin:
        return True                                    # curl vb. araçlar / eski tarayıcılar; yetki zaten ayrıca denetlenir
    try:
        o = origin.split('://', 1)[1].rstrip('/').lower()
    except IndexError:
        return False
    return o == (host_header or '').strip().lower()


# ── 4) PIN denemesi hız sınırı ───────────────────────────

_MAX_FAILS = 5
_LOCK_SEC  = 5 * 60
_fails: dict[str, list] = {}                           # ip -> [başarısız_sayısı, kilit_bitişi]
_flock = threading.Lock()


def login_locked(ip: str) -> int:
    """Kilitliyse kalan saniyeyi, değilse 0 döner."""
    with _flock:
        rec = _fails.get(ip)
        if rec and rec[1] > time.time():
            return int(rec[1] - time.time()) + 1
    return 0


def login_failed(ip: str) -> None:
    with _flock:
        rec = _fails.setdefault(ip, [0, 0.0])
        rec[0] += 1
        if rec[0] >= _MAX_FAILS:
            rec[0] = 0
            rec[1] = time.time() + _LOCK_SEC
        if len(_fails) > 2000:                         # bellek şişmesin
            now = time.time()
            for k in [k for k, v in _fails.items() if v[1] < now and v[0] == 0]:
                _fails.pop(k, None)


def login_succeeded(ip: str) -> None:
    with _flock:
        _fails.pop(ip, None)


# ── 5) Diğer girdi doğrulamaları ─────────────────────────

REMOTE_COMMANDS = {'anthem', 'tribute', 'tribute2min', 'bell', 'stop'}
_RE_BAD_FILENAME = re.compile(r'[\x00-\x1f<>:"`/\\|?*]')


def safe_filename(name: str) -> bool:
    return bool(name) and len(name) <= 150 and not name.startswith('.') and not _RE_BAD_FILENAME.search(name)


def safe_district(code: str) -> bool:
    return bool(re.fullmatch(r'\d{1,6}', code or ''))
