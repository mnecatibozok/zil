#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zil Sistemi — Main Server"""

import os, sys, socket, socketserver

# Bu kod 3.10+ söz dizimi kullanır (örn. `str | None`). Eski Python'da import sırasında anlaşılmaz
# bir TypeError ile çökmek yerine açık bir mesaj verip pencereyi açık tut.
if sys.version_info < (3, 10):
    print(f'[HATA] Python 3.10 veya uzeri gerekli (kurulu: {sys.version.split()[0]}). https://www.python.org/downloads/')
    try:
        input('Cikmak icin Enter...')
    except Exception:
        pass
    sys.exit(1)

# ── Import from this folder ──────────────────────────────
# This file lives in the zunucu/ folder. The modules (utils, ezan, handler)
# are in the same folder, so we add it to sys.path.
_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
if _SERVER_DIR not in sys.path:
    sys.path.insert(0, _SERVER_DIR)

# ── Switch to root directory ─────────────────────────────
# The HTTP server serves from the root directory:
# HTML, zilsesleri/, mp3/, zil-port.txt are all in the root.
_ROOT_DIR = os.path.dirname(_SERVER_DIR)
os.chdir(_ROOT_DIR)

# Konsol çıktısını aynı zamanda dönen bir log dosyasına yaz (zil-sunucu.log, 1 MB x 3 dosya)
import logging, logging.handlers
_file_log = logging.getLogger('zil-sunucu')
_file_log.setLevel(logging.INFO)
_fh = logging.handlers.RotatingFileHandler('zil-sunucu.log', maxBytes=1_000_000, backupCount=3, encoding='utf-8')
_fh.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
_file_log.addHandler(_fh)


class _Tee:
    """stdout/stderr'i hem konsola hem log dosyasına yazar."""
    def __init__(self, stream): self._s = stream
    def write(self, text):
        try:
            if self._s is not None: self._s.write(text)
        except Exception: pass
        if text and text.strip(): _file_log.info(text.rstrip())
    def flush(self):
        try:
            if self._s is not None: self._s.flush()
        except Exception: pass
    def __getattr__(self, name): return getattr(self._s, name)


sys.stdout = _Tee(sys.stdout)
sys.stderr = _Tee(sys.stderr)

from utils         import find_free_port, build_manifest, build_mp3_manifest
from handler       import ZilHandler
import watchdog
from kumanda_auth  import get_or_create_pin

HTML_FILE = 'zil.html'
PORT_FILE = 'zil-port.txt'


def _find_html_file(base_dir: str) -> str | None:
    """Finds the HTML file — exact name or an .html file starting with 'zil-program'."""
    if os.path.exists(os.path.join(base_dir, HTML_FILE)):
        return HTML_FILE
    for f in os.listdir(base_dir):
        fl = f.lower()
        if fl.endswith('.html') and ('zil-program' in fl or 'zil_program' in fl):
            print(f"[ZIL] '{HTML_FILE}' not found, using '{f}'.")
            return f
    return None


def _print_manifest(manifest: list, mp3_manifest: dict) -> None:
    print(f'[ZIL] zilsesleri/ : {len(manifest)} sound files')
    for item in manifest:
        print(f"[ZIL]   + {item['file']}")
    if not manifest:
        print('[ZIL]   (folder empty or missing — create zilsesleri/)')
    for folder, files in mp3_manifest.items():
        print(f'[ZIL] mp3/{folder}/ : {len(files)} tracks')


def _print_network_addresses(port: int, html_file: str) -> None:
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        print(f'[ZIL] Network : http://{local_ip}:{port}/{html_file}')
        print(f'[ZIL] Remote  : http://{local_ip}:{port}/kumanda')
    except Exception:
        pass
    print(f'[ZIL] Kumanda PIN : {get_or_create_pin()}  (kumanda-pin.json dosyasından değiştirilebilir)')


def main() -> None:
    global HTML_FILE

    print(f'[ZIL] Root dir  : {_ROOT_DIR}')
    print(f'[ZIL] Modules   : {_SERVER_DIR}')

    # Find HTML file
    html = _find_html_file(_ROOT_DIR)
    if not html:
        print(f'[ERROR] HTML file not found! Looking for: {HTML_FILE}')
        print(f'[ERROR] Directory contents: {[f for f in os.listdir(_ROOT_DIR) if f.endswith(".html")]}')
        input("Press Enter to continue...")
        sys.exit(1)
    HTML_FILE = html
    print(f'[ZIL] File      : {HTML_FILE}')

    # Manifest
    manifest     = build_manifest(_ROOT_DIR)
    mp3_manifest = build_mp3_manifest(_ROOT_DIR)
    _print_manifest(manifest, mp3_manifest)

    # Port
    port = find_free_port()
    print(f'[ZIL] Port      : {port}')
    try:
        with open(os.path.join(_ROOT_DIR, PORT_FILE), 'w') as pf:
            pf.write(str(port))
    except Exception as e:
        print(f'[WARNING] Could not write port file: {e}')

    # Server
    try:
        socketserver.ThreadingTCPServer.allow_reuse_address = True
        with socketserver.ThreadingTCPServer(('0.0.0.0', port), ZilHandler) as httpd:
            print(f'[ZIL] Ready     : http://localhost:{port}/{HTML_FILE}')
            _print_network_addresses(port, HTML_FILE)
            print('[ZIL] Close this window or press Ctrl+C to stop')
            watchdog.start(port, HTML_FILE)
            httpd.serve_forever()
    except Exception as e:
        print(f'[ERROR] Could not start server: {e}')
        input("Press Enter to continue...")


if __name__ == '__main__':
    main()
