# Değişiklikler — 8 Ekim 2026 (bağımsız denetim sonrası)

- **Ayar yedeği:** Tüm `zil*` localStorage anahtarları (planlar, takvimler, sessiz mod, ezan, anfi, MP3…) `zil-ayarlar.json` dosyasına yansıtılır; günde bir kopya `yedek/` içine alınır (14 gün). Açılışta sunucuda olmayan anahtarlar sunucuya eklenir. Hacimli `zilCalmaGecmisi` ve `zilMp3ZilQueue` hariç.
- **Zamanlayıcı:** `zil-baslat.bat` Chrome'a arka plan/örtülme zamanlayıcı yavaşlatmasını kapatan bayraklar ekler.
- **Bekçi (`zunucu/watchdog.py`):** Sayfa ~5 sn'de bir `/api/heartbeat` çağırır; 90 sn kesilirse kiosk Chrome yeniden açılır (saatte en fazla 5). `/api/exit` ve `/api/shutdown` bekçiyi kapatır. Devre dışı bırakmak için `ZIL_WATCHDOG=0`. **Not:** Alt+F4 ile kapatılan Chrome ~90 sn içinde geri açılır; bilinçli kapatma için programdaki çıkış/kapatma düğmesi kullanılmalı.
- **Anfi:** Arduino bağlı değilken "Anfi Aç" artık sahte "açık" göstermez; Aktivite günlüğüne uyarı düşer.
- **Kapatma (Windows dışı yedek):** `/api/shutdown` komutu başarısız olursa artık sunucuyu kapatmıyor. Linux dalı yalnızca ileride gerekirse diye duruyor; Windows'ta etkisi yok.
- **Anons:** Klasörde olmayan `anons_tenefus.mp3` varsayılanı kaldırıldı (tenefüste anons yok); sunucu/JS/config tutarlı.
- **Anneler Günü:** Tarih seçicideki hızlı buton Mayıs'ın 2. Pazarına gider; 5 Mayıs'ta yanlışlıkla tema görünmez.
- **Log:** Sunucu çıktısı `zil-sunucu.log` dosyasına da yazılır (1 MB × 3 dosya).
- **i18n:** `verify_i18n.py` artık gömülü yedek sözlüklerin locale dosyalarıyla aynı olduğunu da denetler; `python3 verify_i18n.py --yaz` yeniden üretir.

## Arduino güvenlik zaman aşımı (anfi.ino'ya eklendi)
Anfi bilgisayar komutuyla (`ANFI_AC`) açıldıysa ve 120 sn bilgisayardan hiç komut gelmezse röle kapanır, `UYARI:HOST_ZAMAN_ASIMI` yazılır. Zil programı 10 sn'de bir `DURUM` gönderdiği için normalde dolmaz. Butonla elle açılan anfi zaman aşımına tabi değildir. Ayrıca açılışta röle pini önce HIGH yazılıp sonra OUTPUT yapılır (boot'ta kısa tetikleme olmasın). Güncel firmware artık `Arduino/anfi.ino` olarak pakettedir; kartı yeniden yüklemek gerekir.

## RF kumanda CH3 yerel yedek (anfi.ino)
Bilgisayar 25 sn'den uzun süre sessizse (kapalı/çökmüş/hiç bağlanmamış) RF CH3 anfiyi doğrudan Arduino'da aç/kapatır ve `ANFI:YEREL_TOGGLE` yazar; bu şekilde açılan anfi buton gibi elle açılmış sayılır (zaman aşımı yok). Bilgisayar canlıyken CH3 eskisi gibi yalnızca `ANFI:TOGGLE` yollar. CH1/CH2/CH4 (Marş, Zil, DUR) ses gerektirdiği için bilgisayara bağlı kalır.
