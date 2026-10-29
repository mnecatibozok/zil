# i18n Migration — İlerleme Takibi

## Durum: TAMAMLANDI (7 Ekim 2026) — `verify_i18n.py` tüm anahtarların TR/EN dosyalarında bulunduğunu doğrular

## Kurulu altyapı (TAMAMLANDI)
- `i18n(key, params)` JS fonksiyonu — locales/*.json içinden nokta-yollu
  (dot-path) anahtar okur.
- `data-i18n="key"` → textContent değiştirir
- `data-i18n-html="key"` → innerHTML değiştirir (örn. `<br>` içeren metinler)
- `data-i18n-placeholder="key"`, `data-i18n-title="key"` → ilgili attribute
- `setLanguage('en')` → dili değiştirir, localStorage'a kaydeder, sayfayı
  yeniden render eder
- Sidebar'da TR/EN buton ile dil seçici (görsel)
- `_i18nInit()` → `init()` fonksiyonunun en başında çağrılıyor, tarayıcı
  dilini veya kayıtlı tercihi otomatik algılıyor
- `locales/tr.json`, `locales/en.json` — backend zaten statik dosya
  servisi yaptığı için ekstra backend kodu gerekmedi
- `verify_i18n.py` — HER bölüm tamamlandığında çalıştırılmalı. HTML/JS
  içindeki TÜM data-i18n* ve i18n() referanslarının her iki dil
  dosyasında da karşılığı olduğunu doğrular.

## Tamamlanan bölümler
- [x] Sidebar (sb-lbl etiketleri, dinamik Zil Durdur/Devam, Anfi Açık/Kapalı)
- [x] Topbar (başlık, "Yükleniyor…", "Sonraki Zil", özel gün butonu, title'lar)
- [x] Program Tab (ses çubuğu, VU metre, hızlı butonlar, MP3 kartı, program tablosu)

## Sırada
- Yok. Yeni UI metni eklerken: önce `locales/tr.json` ve `locales/en.json`'a anahtar ekleyin, sonra
  gömülü `_I18N_TR_FALLBACK` / `_I18N_EN_FALLBACK` sözlüklerini dil dosyalarından yeniden üretin.

## Önemli notlar / dikkat edilecekler
- `ampUIUpdate()` fonksiyonu (satır ~6665+) çok sayıda dinamik metin
  içeriyor (txt.textContent, sub.textContent, portLabel.textContent) —
  Anfi ayar paneli bölümüne geçildiğinde bunlarla birlikte ele alınmalı.
- Bazı statik metinler JS tarafından ilk render sonrası ezilir (örn.
  stMain, nextLabel) — data-i18n eklemek zararsız (sadece ilk anlık görünüm
  için) ama gerçek çeviri JS'deki i18n() çağrılarından gelmeli.
- Marka/kişisel isimler (örn. "Mustafa Necati BOZOK", okul adı, "Temmuz
  2026" gibi statik info) çevrilmemeli — bunlar veri, UI metni değil.
- Her bölümü bitirdikten sonra MUTLAKA:
  1. `python3 verify_i18n.py` çalıştır (her iki dilde anahtar eksik mi kontrol)
  2. `node --check` ile JS sözdizimi doğrula (script bloğunu sed ile çıkarıp)
  3. Mümkünse gerçek sunucu ile entegrasyon testi yap
