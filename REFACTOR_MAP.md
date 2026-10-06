# Refactor Mapping — Turkish → English identifiers

## STATUS: Backend ✅ tamamlandı · Frontend (zil.html) ✅ tamamlandı

Bu dosya, projeyi dilden bağımsız hale getirme refactor'unun referans
tablosudur. Hem backend (Python) hem frontend (zil.html) artık bu tabloya
göre güncellenmiştir.

### Frontend refactor özeti
- 320 fonksiyon adı, 268 DOM id, 77 global değişken İngilizceye çevrildi
  (otomatik script + word-boundary regex ile, build_function_map.py /
  build_id_map.py / build_global_var_map.py / apply_renames.py).
- API endpoint string literal'ları backend ile eşleştirildi
  (`/api/anons-ayar` → `/api/announcement-config` vb.)
- Bell/announcement sound-key sistemi İngilizceleştirildi
  (`zil`→`bell`, `mars`→`anthem`, `saygi`→`tribute`, `depremIkaz`→`alarmAlert` vb.)
- Announcement-type sistemi İngilizceleştirildi
  (`ogretmen`→`teacher`, `ogrenci`→`student`, `toplanma`→`assembly`,
  `sonZil`→`lastBell`, `tenefus`→`break`)
- MP3 zil matrisi İngilizceleştirildi (`dersEnd`→`lessonEnd`, `ogrenci`→`student`,
  `ogretmen`→`teacher`)
- Plan C grup-arası tipi İngilizceleştirildi (`ara: 'tenefus'|'ogle'|'yok'`
  → `'break'|'noon'|'none'`)
- **Dinamik ID/anahtar üretim noktaları** (`getElementById('prefix_'+var)`,
  literal-array `.forEach()` kalıpları) tek tek elle incelenip backend/HTML
  ile senkronize edildi — bunlar otomatik regex'in yakalayamadığı, en riskli
  noktalardı (switchTab, switchSettingsTab, switchLogSubTab, alarmBar,
  mp3DurationMode, mp3Matrix, prayer-time inputs, Plan B/C ayar formları).

### Kasıtlı olarak Türkçe bırakılanlar (karar gereği)
- `ezan.py` içeriği: Diyanet/Haberturk/NTV/Aladhan entegrasyonu ve
  `imsak/gunes/ogle/ikindi/aksam/yatsi` terimleri — din/kültüre özgü, normal
  bir "çeviri" gerektirmiyor; frontend'de `PRAYER_TIME_NAMES` /
  `PRAYER_TIME_ID_SUFFIX` ile DOM id'lere köprülendi.
- `daySettings`/`_planBSettings`/`_planCSettings` programı zamanlama şeması
  (`top`, `topSure`, `ilk`, `dSure`, `ogleA`, `ogleK`, `ogretmenErken`) —
  48+ kullanım yeri ve `top` aleminin CSS `style.top` ile isim çakışması
  riski nedeniyle bilinçli olarak değiştirilmedi. Yalnızca DOM id
  senkronizasyonu (`pb_`/`pc_` + suffix-map) düzeltildi.
- `zunucu/`, `zilsesleri/` klasör adları — geriye dönük uyumluluk için.

### Bilinen, refactor'dan bağımsız önceden var olan kusurlar
- `tblTitle`, `zilPlayerNowName` id'leri JS'de `getElementById` ile
  aranıyor ama HTML'de tanımlı değil (orijinal dosyada da böyleydi,
  `?.` ile güvenli kullanılmış, kırılma yaratmıyor).

---

This is the single source of truth for renames across backend (Python) and,
later, frontend (JS). Keep frontend changes in sync with this table.

## Bell/announcement type keys (JSON config keys, used in zil-ses-ayar.json,
## zil-anons-ayar.json, and as dict keys in Python + JS)

| Old (TR)        | New (EN)       | Meaning                          |
|-----------------|----------------|-----------------------------------|
| `zil`           | `bell`         | Generic bell                      |
| `zilTenefus`    | `bellBreak`    | Break/recess bell                 |
| `zilOgrenci`    | `bellStudent`  | Student bell                      |
| `zilOgretmen`   | `bellTeacher`  | Teacher bell                      |
| `zilToplanma`   | `bellAssembly` | Assembly bell                     |
| `mars`          | `anthem`       | National anthem                   |
| `saygi`         | `tribute`      | Moment of silence (1 min)         |
| `saygi2dk`      | `tribute2min`  | Moment of silence (2 min)         |
| `depremIkaz`    | `alarmAlert`   | Earthquake/emergency alert sound  |
| `depremTahliye` | `alarmEvacuate`| Evacuation sound                  |
| `ogretmen`      | `teacher`      | Teacher announcement key          |
| `ogrenci`       | `student`      | Student announcement key          |
| `toplanma`      | `assembly`     | Assembly announcement key         |
| `sonZil`        | `lastBell`     | End-of-day announcement key       |
| `tenefus`       | `break`        | Break announcement key            |

## API response fields

| Old (TR) | New (EN)  |
|----------|-----------|
| `hata`   | `error`   |
| `uyari`  | `warning` |
| `mesaj`  | `message` |
| `ayar`   | `config`  |
| `ok`     | `ok` (unchanged — already neutral) |
| `cmd`    | `cmd` (unchanged — already neutral) |
| `kaynak` | `source`  |
| `tarih`  | `date`    |
| `vakitler` | `times` |

## API endpoints

| Old                       | New                          |
|----------------------------|------------------------------|
| `/api/anons-ayar`          | `/api/announcement-config`   |
| `/api/zil-ses-ayar`        | `/api/bell-sound-config`     |
| `/api/ezan-vakitleri`      | `/api/prayer-times`          |
| `/api/kumanda`             | `/api/remote`                |
| `/api/kumanda-poll`        | `/api/remote-poll`           |
| `/api/ses-yukle`           | `/api/sound-upload`          |
| `/api/move-to-temp`        | `/api/move-to-temp` (unchanged — already neutral) |
| `/api/restore-from-temp`   | `/api/restore-from-temp` (unchanged) |
| `/api/blacklist`           | `/api/blacklist` (unchanged) |
| `/api/ntp-kontrol`         | `/api/ntp-check`             |
| `/api/exit`, `/api/shutdown` | unchanged                  |

## File names (config files written to disk)

| Old                      | New                       |
|---------------------------|---------------------------|
| `zil-anons-ayar.json`      | `bell-announcement-config.json` |
| `zil-ses-ayar.json`        | `bell-sound-config.json`  |

## Prayer-time query params (kept Turkish-API-compatible internally, but
## response keys translated)

| Old        | New      |
|------------|----------|
| `ilce`     | `district` (query param — kept as-is internally since it maps to Diyanet's own ilce code; only exposed name changes if we touch query parsing) |
| `il`       | `province` |
| `vakitler` (dict keys) `imsak,gunes,ogle,ikindi,aksam,yatsi` | kept as-is — these are religious term names, not generic identifiers, and have no clean single-word English equivalent without losing meaning. Per project decision, ezan.py internals (logic + Diyanet/Aladhan integration) are left functionally as-is; we only rename **generic** plumbing identifiers, not domain-specific religious vocabulary. |

## Python module/function names

| Old                  | New                  |
|------------------------|------------------------|
| `vakit_cek`            | `fetch_prayer_times`  |
| `load_anons_ayar`      | `load_announcement_config` |
| `save_anons_ayar`      | `save_announcement_config` |
| `load_zil_ses_ayar`    | `load_bell_sound_config` |
| `save_zil_ses_ayar`    | `save_bell_sound_config` |
| `build_manifest`       | unchanged (already EN) |
| `build_mp3_manifest`   | unchanged |
| `ntp_offset_saniye`    | `ntp_offset_seconds`  |
| `find_free_port`       | unchanged |
| `slugify_tr`           | unchanged (already EN, "tr" = generic transliteration suffix, fine) |
| `ascii_upper_tr`       | unchanged |
| `parse_first6`         | unchanged |

## Folder names (left as-is for now — large user-facing rename / breaks
## existing installs; flagged for a later, separate pass)

- `zunucu/` (= "sunucu" = server) — recommend renaming to `server/` in a later pass
- `zilsesleri/` (= bell sounds) — recommend renaming to `sounds/` in a later pass

These are deferred because renaming folders breaks file paths referenced
throughout zil.html and the .bat launcher; doing it together with the
frontend pass (next step) avoids a half-migrated state.
