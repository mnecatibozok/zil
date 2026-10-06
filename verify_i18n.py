#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifies that every data-i18n / data-i18n-html / data-i18n-placeholder /
data-i18n-title key referenced in zil.html (including i18n('...') JS calls)
exists in both locales/tr.json and locales/en.json, and reports orphaned
locale keys (present in JSON but unused in HTML/JS) for cleanup awareness."""
import re, json, sys

with open('zil.html', encoding='utf-8') as f:
    html = f.read()

with open('locales/tr.json', encoding='utf-8') as f:
    tr = json.load(f)
with open('locales/en.json', encoding='utf-8') as f:
    en = json.load(f)


def flatten(d, prefix=''):
    keys = set()
    for k, v in d.items():
        if k == '_meta':
            continue
        full = f'{prefix}.{k}' if prefix else k
        if isinstance(v, dict):
            keys |= flatten(v, full)
        else:
            keys.add(full)
    return keys


tr_keys = flatten(tr)
en_keys = flatten(en)

# Keys referenced in HTML attributes
html_keys = set(re.findall(r'data-i18n(?:-html|-placeholder|-title)?="([a-zA-Z0-9_.]+)"', html))
html_keys -= {'key', 'key.path'}
# Keys referenced via i18n('...') JS calls
js_keys = set(re.findall(r"i18n\('([a-zA-Z0-9_.]+)'", html))
# Exclude doc-comment placeholder examples (not real keys)
js_keys -= {'key', 'key.path'}

used_keys = html_keys | js_keys

missing_in_tr = used_keys - tr_keys
missing_in_en = used_keys - en_keys
unused_in_tr = tr_keys - used_keys
unused_in_en = en_keys - used_keys

print(f"Used keys (HTML attrs + JS i18n() calls): {len(used_keys)}")
print(f"  from data-i18n*  attrs: {len(html_keys)}")
print(f"  from i18n() calls:      {len(js_keys)}")
print(f"tr.json keys: {len(tr_keys)}")
print(f"en.json keys: {len(en_keys)}")

ok = True
if missing_in_tr:
    ok = False
    print(f"\n❌ MISSING in tr.json ({len(missing_in_tr)}):")
    for k in sorted(missing_in_tr):
        print("   -", k)
if missing_in_en:
    ok = False
    print(f"\n❌ MISSING in en.json ({len(missing_in_en)}):")
    for k in sorted(missing_in_en):
        print("   -", k)
if unused_in_tr:
    print(f"\n⚠️  Unused tr.json keys ({len(unused_in_tr)}) — not an error, just FYI:")
    for k in sorted(unused_in_tr):
        print("   -", k)

if ok:
    print("\n✅ All referenced keys exist in both locale files.")
else:
    sys.exit(1)
