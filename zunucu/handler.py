#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zil Sistemi — HTTP Handler (GET / POST routes)"""

import http.server, json, os, shutil, subprocess, threading, time, urllib.parse, base64

from utils        import build_manifest, build_mp3_manifest, ntp_offset_seconds
from ezan         import fetch_prayer_times
from zilsesler    import (load_announcement_config, save_announcement_config,
                           load_bell_sound_config, save_bell_sound_config)
from app_settings import load_all_settings, save_one_setting
from kumanda_auth import (get_or_create_pin, verify_pin, create_session,
                           is_valid_session, parse_cookie, COOKIE_NAME, SESSION_TTL)

# Remote control command — in-process memory (poll mechanism)
_remote_cmd  : str   = ''
_remote_ts   : float = 0.0
_remote_lock : threading.Lock = threading.Lock()

# Remote control HTML page (inline — no extra file needed)
_REMOTE_HTML = """\
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Zil Kumanda</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: sans-serif; background: #0e1117; color: #fff;
      min-height: 100vh; display: flex; flex-direction: column;
      align-items: center; justify-content: center; gap: 16px; padding: 20px;
    }
    h1 { font-size: 1.2rem; opacity: .7; }
    .btn {
      width: 220px; padding: 20px; border-radius: 16px; border: none;
      font-size: 1.3rem; font-weight: 800; cursor: pointer;
      transition: transform .15s, box-shadow .15s; text-align: center;
    }
    .btn:active { transform: scale(.95); }
    .mars   { background: linear-gradient(135deg,#dc2626,#991b1b); color:#fff; box-shadow: 0 4px 20px rgba(220,38,38,.4); }
    .saygi  { background: linear-gradient(135deg,#7c3aed,#5b21b6); color:#fff; box-shadow: 0 4px 20px rgba(124,58,237,.4); }
    .zil    { background: linear-gradient(135deg,#16a34a,#15803d); color:#fff; box-shadow: 0 4px 20px rgba(22,163,74,.4); }
    .dur    { background: linear-gradient(135deg,#374151,#1f2937); color:#ef4444; border: 2px solid #ef4444; box-shadow: 0 4px 20px rgba(239,68,68,.3); }
    .status { font-size: .8rem; color: #888; text-align: center; }
    .lang-row { display:flex; gap:8px; }
    .lang-btn { padding:4px 10px; border-radius:6px; border:1px solid #334155; background:transparent; color:#888; font-size:.7rem; font-weight:700; cursor:pointer; }
    .lang-btn.active { background:#3b82f6; color:#fff; border-color:#3b82f6; }
  </style>
</head>
<body>
  <h1 id="t_title">🔔 Zil Kumanda</h1>
  <div class="lang-row">
    <button class="lang-btn active" onclick="setLang('tr')">TR</button>
    <button class="lang-btn" onclick="setLang('en')">EN</button>
  </div>
  <button class="btn mars"  onclick="cmd('anthem')" id="t_anthem">🎖 İstiklâl Marşı</button>
  <button class="btn saygi" onclick="cmd('tribute')" id="t_tribute">🤲 Saygı Duruşu 1dk</button>
  <button class="btn saygi" onclick="cmd('tribute2min')" style="opacity:.85" id="t_tribute2">🤲 Saygı Duruşu 2dk</button>
  <button class="btn zil"   onclick="cmd('bell')" id="t_bell">🔔 Zil Çal</button>
  <button class="btn dur"   onclick="cmd('stop')" id="t_stop">⏹ DURDUR</button>
  <div class="status" id="st" data-connected="Bağlı" data-connected-en="Connected">Bağlı</div>
  <script>
    const LABELS = {
      tr: { title:'🔔 Zil Kumanda', anthem:'🎖 İstiklâl Marşı', tribute:'🤲 Saygı Duruşu 1dk', tribute2:'🤲 Saygı Duruşu 2dk', bell:'🔔 Zil Çal', stop:'⏹ DURDUR', sending:'Gönderiliyor...', connected:'Bağlı', conn_err:'❌ Bağlantı hatası' },
      en: { title:'🔔 Bell Remote', anthem:'🎖 National Anthem', tribute:'🤲 Tribute 1min', tribute2:'🤲 Tribute 2min', bell:'🔔 Ring Bell', stop:'⏹ STOP', sending:'Sending...', connected:'Connected', conn_err:'❌ Connection error' }
    };
    let _lang = localStorage.getItem('kumandaLang') || 'tr';

    function setLang(lang) {
      _lang = lang;
      localStorage.setItem('kumandaLang', lang);
      const L = LABELS[lang] || LABELS.tr;
      document.getElementById('t_title').textContent   = L.title;
      document.getElementById('t_anthem').textContent  = L.anthem;
      document.getElementById('t_tribute').textContent = L.tribute;
      document.getElementById('t_tribute2').textContent= L.tribute2;
      document.getElementById('t_bell').textContent    = L.bell;
      document.getElementById('t_stop').textContent    = L.stop;
      const st = document.getElementById('st');
      if(st.textContent === LABELS[_lang === 'tr' ? 'en' : 'tr'].connected || st.textContent === LABELS[_lang].connected)
        st.textContent = L.connected;
      document.documentElement.setAttribute('lang', lang);
      document.querySelectorAll('.lang-btn').forEach(b => b.classList.toggle('active', b.textContent === lang.toUpperCase()));
    }

    setLang(_lang);

    async function cmd(key) {
      const L = LABELS[_lang] || LABELS.tr;
      const st = document.getElementById('st');
      try {
        st.textContent = L.sending;
        const r = await fetch('/api/remote', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ cmd: key }),
        });
        const d = await r.json();
        st.textContent = d.ok ? '✅ ' + d.message : '❌ ' + d.error;
      } catch (e) {
        st.textContent = L.conn_err;
      }
      setTimeout(() => { st.textContent = L.connected; }, 3000);
    }
  </script>
</body>
</html>
"""

# PIN giriş sayfası — oturum çerezi yoksa/geçersizse bu gösterilir
_LOGIN_HTML = """\
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Zil Kumanda — Giriş</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: sans-serif; background: #0e1117; color: #fff;
      min-height: 100vh; display: flex; flex-direction: column;
      align-items: center; justify-content: center; gap: 14px; padding: 20px;
    }
    h1 { font-size: 1.1rem; opacity: .8; }
    input {
      width: 220px; padding: 14px; border-radius: 10px; border: 2px solid #334155;
      background: #1a1f2b; color: #fff; font-size: 1.4rem; text-align: center;
      letter-spacing: 4px;
    }
    input:focus { outline: none; border-color: #3b82f6; }
    button {
      width: 220px; padding: 14px; border-radius: 10px; border: none;
      background: #3b82f6; color: #fff; font-size: 1rem; font-weight: 700;
      cursor: pointer;
    }
    button:active { transform: scale(.97); }
    .err { color: #ef4444; font-size: .85rem; min-height: 1.2em; }
  </style>
</head>
<body>
  <h1>🔒 Zil Kumanda — PIN Girin</h1>
  <input id="pin" type="password" inputmode="numeric" maxlength="6" autofocus placeholder="••••••">
  <button onclick="login()">Giriş</button>
  <div class="err" id="err"></div>
  <script>
    async function login() {
      const pin = document.getElementById('pin').value.trim();
      const err = document.getElementById('err');
      if(!pin) return;
      try {
        const r = await fetch('/api/kumanda-login', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pin }),
        });
        const d = await r.json();
        if(d.ok) { location.reload(); }
        else { err.textContent = d.error || 'Hatalı PIN'; }
      } catch(e) { err.textContent = 'Bağlantı hatası'; }
    }
    document.getElementById('pin').addEventListener('keydown', e => { if(e.key === 'Enter') login(); });
  </script>
</body>
</html>
"""


class ZilHandler(http.server.SimpleHTTPRequestHandler):

    # ── Logging ──────────────────────────────────────────

    def log_message(self, fmt, *args):
        if hasattr(self, 'path') and 'favicon' in self.path:
            return
        if args and len(args) >= 2 and str(args[1]) not in ('200', '304', '206'):
            print(f'[ZIL] {self.path} → {args[1]}')

    # ── GET ───────────────────────────────────────────────

    def do_GET(self):
        path   = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
        parsed = urllib.parse.urlparse(self.path)

        if path == '/ses-manifest.json':
            return self._serve_json(build_manifest(os.getcwd()))

        if path == '/mp3-manifest.json':
            return self._serve_json(build_mp3_manifest(os.getcwd()))

        if path == '/api/prayer-times':
            return self._get_prayer_times(parsed)

        if path == '/api/remote-poll':
            return self._get_remote_poll()

        if path == '/api/blacklist':
            return self._get_blacklist()

        if path == '/api/ntp-check':
            return self._get_ntp_check()

        if path == '/api/announcement-config':
            return self._serve_json(load_announcement_config())

        if path == '/api/bell-sound-config':
            return self._serve_json(load_bell_sound_config())

        if path == '/api/app-settings':
            return self._serve_json({'ok': True, 'settings': load_all_settings()})

        if path in ('/kumanda', '/kumanda.html'):
            token = parse_cookie(self.headers.get('Cookie'))
            if is_valid_session(token):
                return self._serve_html(_REMOTE_HTML)
            return self._serve_html(_LOGIN_HTML)

        super().do_GET()

    def _get_ntp_check(self):
        offset = ntp_offset_seconds()
        if offset is None:
            self._serve_json({'ok': False, 'error': 'Could not reach NTP server'})
            return
        warning = abs(offset) >= 30
        self._serve_json({
            'ok'     : True,
            'offset' : offset,
            'warning': warning,
            'message': f'System clock is {offset:+.1f}s {"ahead" if offset > 0 else "behind"} NTP' if warning
                       else f'System clock is accurate (±{abs(offset):.1f}s)',
        })

    def _get_prayer_times(self, parsed):
        qs       = urllib.parse.parse_qs(parsed.query)
        district = qs.get('ilce',   ['9541'])[0]
        province = qs.get('il',     [''])[0]
        source   = qs.get('kaynak', [''])[0]
        print(f'[PRAYER] Request — province: {province}, district: {district}, source: {source}')
        self._serve_json(fetch_prayer_times(district, province, source))

    def _get_remote_poll(self):
        global _remote_cmd, _remote_ts
        cmd = ''
        with _remote_lock:
            if _remote_cmd and (time.time() - _remote_ts) < 5:
                cmd = _remote_cmd
                _remote_cmd = ''
        self._serve_json({'cmd': cmd})

    def _get_blacklist(self):
        self._serve_json({'ok': True, 'blacklist': _load_blacklist()})

    # ── POST ──────────────────────────────────────────────

    def do_POST(self):
        path = self.path.split('?')[0]
        print(f'[API] POST → {path}')

        length = int(self.headers.get('Content-Length', 0))
        raw    = self.rfile.read(length) if length else b'{}'
        try:
            body = json.loads(raw.decode('utf-8'))
        except Exception:
            body = {}

        if '/api/move-to-temp' in path:
            return self._post_move_to_temp(body)

        if '/api/restore-from-temp' in path:
            return self._post_restore_from_temp(body)

        if '/api/blacklist' in path:
            return self._post_blacklist(body)

        if path == '/api/kumanda-login':
            return self._post_kumanda_login(body)

        if '/api/remote' in path and '/remote-poll' not in path:
            token = parse_cookie(self.headers.get('Cookie'))
            if not is_valid_session(token):
                self.send_response(401)
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
            return self._post_remote(body)

        if path == '/api/announcement-config':
            return self._post_announcement_config(body)

        if path == '/api/bell-sound-config':
            return self._post_bell_sound_config(body)

        if path == '/api/app-settings':
            return self._post_app_settings(body)

        if path == '/api/sound-upload':
            return self._post_sound_upload(body)

        if '/api/exit' in path:
            return self._post_exit()

        if '/api/shutdown' in path:
            return self._post_shutdown()

        print(f'[API] 404: {path}')
        self._serve_json({'ok': False, 'error': f'Unknown endpoint: {path}'})

    def _post_move_to_temp(self, body):
        filepath = body.get('path', '')
        print(f'[MOVE] path: "{filepath}"')
        if not filepath:
            return self._serve_json({'ok': False, 'error': 'path is empty'})

        cwd  = os.path.realpath(os.getcwd())
        full = os.path.realpath(os.path.join(cwd, filepath))

        if not full.startswith(cwd + os.sep):
            print(f'[MOVE] SECURITY: disallowed path: {full}')
            return self._serve_json({'ok': False, 'error': 'Invalid path'})

        print(f'[MOVE] full path: "{full}"  — exists: {os.path.exists(full)}')

        if not os.path.isfile(full):
            return self._serve_json({'ok': False, 'error': f'File not found: {filepath}'})

        temp_dir = os.path.join(cwd, 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        fname = os.path.basename(full)
        dest  = os.path.join(temp_dir, fname)
        if os.path.exists(dest):
            base, ext = os.path.splitext(fname)
            n = 1
            while os.path.exists(os.path.join(temp_dir, f'{base}_{n}{ext}')):
                n += 1
            dest = os.path.join(temp_dir, f'{base}_{n}{ext}')

        try:
            shutil.move(full, dest)
            with open(dest + '.origin', 'w', encoding='utf-8') as f:
                f.write(filepath)
            msg = f'{fname} → moved to temp/'
            print(f'[MOVE] OK: {msg}')
            self._serve_json({'ok': True, 'message': msg})
        except Exception as e:
            print(f'[MOVE] ERROR: {e}')
            self._serve_json({'ok': False, 'error': str(e)})

    def _post_restore_from_temp(self, body):
        name = body.get('name', '')
        if not name:
            return self._serve_json({'ok': False, 'error': 'name is empty'})

        cwd      = os.path.realpath(os.getcwd())
        temp_dir = os.path.join(cwd, 'temp')
        src      = None

        if os.path.isdir(temp_dir):
            for f in os.listdir(temp_dir):
                if f.startswith(name) or os.path.splitext(f)[0] == name:
                    src = os.path.join(temp_dir, f)
                    break

        if not src or not os.path.isfile(src):
            return self._serve_json({'ok': False, 'error': 'Not found in temp/'})

        origin_file   = src + '.origin'
        original_path = None
        if os.path.isfile(origin_file):
            with open(origin_file, 'r', encoding='utf-8') as f:
                original_path = f.read().strip()

        if original_path:
            dest_full = os.path.realpath(os.path.join(cwd, original_path))
            if not dest_full.startswith(cwd + os.sep):
                print(f'[RESTORE] SECURITY: disallowed destination: {dest_full}')
                return self._serve_json({'ok': False, 'error': 'Invalid destination path'})
            dest_dir  = os.path.dirname(dest_full)
        else:
            dest_dir  = os.path.join(cwd, 'mp3')
            dest_full = os.path.join(dest_dir, os.path.basename(src))

        os.makedirs(dest_dir, exist_ok=True)
        try:
            shutil.move(src, dest_full)
            if os.path.isfile(origin_file):
                os.remove(origin_file)
            self._serve_json({'ok': True, 'message': f'{name} restored → {os.path.relpath(dest_full, cwd)}'})
        except Exception as e:
            self._serve_json({'ok': False, 'error': str(e)})

    def _post_blacklist(self, body):
        bl     = _load_blacklist()
        action = body.get('action', 'list')
        name   = body.get('name', '')
        if action == 'add' and name and name not in bl:
            bl.append(name)
        elif action == 'remove' and name:
            bl = [x for x in bl if x != name]
        if action in ('add', 'remove'):
            _save_blacklist(bl)
        self._serve_json({'ok': True, 'blacklist': bl})

    def _post_kumanda_login(self, body):
        pin = str(body.get('pin', ''))
        if not verify_pin(pin):
            print('[KUMANDA] Hatalı PIN denemesi')
            return self._serve_json({'ok': False, 'error': 'Hatalı PIN'})
        token = create_session()
        body_bytes = json.dumps({'ok': True}, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body_bytes)))
        self.send_header('Set-Cookie', f'{COOKIE_NAME}={token}; Path=/; Max-Age={SESSION_TTL}; HttpOnly; SameSite=Lax')
        self.end_headers()
        self.wfile.write(body_bytes)
        print('[KUMANDA] Giriş başarılı — yeni oturum açıldı')

    def _post_remote(self, body):
        global _remote_cmd, _remote_ts
        cmd = body.get('cmd', '')
        with _remote_lock:
            _remote_cmd = cmd
            _remote_ts  = time.time()
        print(f'[REMOTE] {cmd}')
        self._serve_json({'ok': True, 'message': f'{cmd} command received', 'cmd': cmd})

    def _post_announcement_config(self, body):
        try:
            data = save_announcement_config(body)
            print(f'[ZIL] Announcement settings saved: {data}')
            self._serve_json({'ok': True, 'config': data})
        except Exception as e:
            self._serve_json({'ok': False, 'error': str(e)})

    def _post_bell_sound_config(self, body):
        try:
            data = save_bell_sound_config(body)
            print(f'[ZIL] Bell sound settings saved: {data}')
            self._serve_json({'ok': True, 'config': data})
        except Exception as e:
            self._serve_json({'ok': False, 'error': str(e)})

    def _post_app_settings(self, body):
        """localStorage'daki bir ayarı sunucu diskine (zil-ayarlar.json) yedekler.
        Body: {"key": "...", "value": <herhangi bir JSON değeri>}"""
        key = body.get('key', '')
        if 'value' not in body:
            return self._serve_json({'ok': False, 'error': 'value alani eksik'})
        try:
            data = save_one_setting(key, body.get('value'))
            self._serve_json({'ok': True, 'settings': data})
        except ValueError as e:
            self._serve_json({'ok': False, 'error': str(e)})
        except Exception as e:
            print(f'[ZIL] ERROR — app-settings: {e}')
            self._serve_json({'ok': False, 'error': str(e)})

    def _post_sound_upload(self, body):
        """Permanently writes a bell sound selected in the settings panel to
        the zilsesleri/ folder. This way the selection persists across
        restarts and page reloads — autoFetchSounds() finds the file
        automatically from the folder next time."""
        try:
            filename = os.path.basename(body.get('filename', '') or '')
            data_b64 = body.get('data', '') or ''

            if not filename or not data_b64:
                return self._serve_json({'ok': False, 'error': 'filename or data missing'})

            allowed_ext = ('.mp3', '.m4a', '.aac', '.ogg', '.wav', '.flac')
            if not filename.lower().endswith(allowed_ext):
                return self._serve_json({'ok': False, 'error': 'Unsupported audio extension'})

            try:
                raw_bytes = base64.b64decode(data_b64)
            except Exception:
                return self._serve_json({'ok': False, 'error': 'Invalid base64 data'})

            if len(raw_bytes) > 50 * 1024 * 1024:
                return self._serve_json({'ok': False, 'error': 'File too large (>50MB)'})

            cwd       = os.path.realpath(os.getcwd())
            sound_dir = os.path.join(cwd, 'zilsesleri')
            os.makedirs(sound_dir, exist_ok=True)
            dest = os.path.join(sound_dir, filename)

            with open(dest, 'wb') as f:
                f.write(raw_bytes)

            print(f'[ZIL] Sound file saved permanently: zilsesleri/{filename} ({len(raw_bytes)} bytes)')
            self._serve_json({'ok': True, 'file': filename, 'path': f'zilsesleri/{filename}'})
        except Exception as e:
            print(f'[ZIL] ERROR — sound-upload: {e}')
            self._serve_json({'ok': False, 'error': str(e)})

    def _post_exit(self):
        self._serve_json({'ok': True, 'message': 'Shutting down server...'})
        print('[ZIL] Exit request — server shutting down.')
        def _exit():
            try:
                subprocess.run(
                    ['wmic', 'process', 'where',
                     "commandline like '%ZilSistemi%'",
                     'call', 'terminate'],
                    capture_output=True, timeout=3
                )
            except Exception:
                pass
            self.server.shutdown()
            os._exit(0)
        threading.Timer(0.3, _exit).start()

    def _post_shutdown(self):
        self._serve_json({'ok': True, 'message': 'Shutting down system...'})
        print('[ZIL] Shutdown request — system shutting down.')
        def _shutdown():
            self.server.shutdown()
            try:
                subprocess.run(
                    ['shutdown', '/s', '/t', '10', '/f', '/c', 'Zil Sistemi automatic shutdown'],
                    check=False,
                )
            except Exception as e:
                print(f'[ERROR] Shutdown: {e}')
        threading.Timer(0.5, _shutdown).start()

    # ── Response helpers ────────────────────────────────

    def _serve_json(self, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type',   'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_html(self, html: str):
        body = html.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type',   'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ── CORS ─────────────────────────────────────────────

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin',  '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Accept-Ranges',  'bytes')
        self.send_header('Cache-Control',  'no-cache')
        super().end_headers()


# ── Blacklist helpers ──────────────────────────────────────

def _blacklist_path() -> str:
    return os.path.join(os.getcwd(), 'blacklist.json')

def _load_blacklist() -> list:
    p = _blacklist_path()
    if os.path.exists(p):
        try:
            with open(p, 'r', encoding='utf-8') as f:
                return json.loads(f.read())
        except Exception:
            pass
    return []

def _save_blacklist(bl: list) -> None:
    with open(_blacklist_path(), 'w', encoding='utf-8') as f:
        f.write(json.dumps(bl, ensure_ascii=False))
