> Güncelleme tarihi: 20 Haziran 2026

# 🔔 Okul Zil Sistemi

Okullarda ders saatlerini, tenefüsleri, İstiklâl Marşı törenlerini ve deprem tatbikatlarını otomatik yöneten, **Arduino destekli akıllı zil sistemi**. Program bir bilgisayardan çalışır; ses kartı üzerinden mevcut anfi/hoparlör sistemine bağlanır. Zil saatleri web arayüzünden kolayca ayarlanır, RF kumandayla uzaktan kontrol edilir.

---

## 📋 İçindekiler

1. [Sistem Nasıl Çalışır?](#-sistem-nasıl-çalışır)
2. [Gereksinimler](#-gereksinimler)
3. [Kurulum (Adım Adım)](#-kurulum-adım-adım)
4. [Klasör Yapısı](#-klasör-yapısı)
5. [Programı Başlatma](#-programı-başlatma)
6. [Web Arayüzü — Sekme Sekme Açıklama](#-web-arayüzü--sekme-sekme-açıklama)
7. [Zil Planları (A / B / C)](#-zil-planları-a--b--c)
8. [Anfi (Amplifikatör) Kontrolü](#-anfi-amplifikatör-kontrolü)
9. [Arduino Bağlantı Şeması](#-arduino-bağlantı-şeması)
10. [RF Uzaktan Kumanda](#-rf-uzaktan-kumanda)
11. [Ses Dosyaları](#-ses-dosyaları)
12. [Deprem Tatbikatı Modu](#-deprem-tatbikatı-modu)
13. [Ezan Entegrasyonu](#-ezan-entegrasyonu)
14. [Sık Sorulan Sorular](#-sık-sorulan-sorular)
15. [Sorun Giderme](#-sorun-giderme)
16. [Sürüm Notları](#-sürüm-notları)

---

## 🧠 Sistem Nasıl Çalışır?

```
[zil-baslat.bat]
       │
       ├──▶ [Python Sunucu] ──▶ localhost:PORT üzerinden dosyaları ve API'yi sunar
       │         │
       │         └──▶ zil-port.txt'e port numarasını yazar
       │
       └──▶ [Google Chrome] ──▶ http://localhost:PORT/zil.html
                   │
                   ├── Zil programını gösterir (tarayıcı = kontrol paneli)
                   ├── Seri port (USB) üzerinden Arduino'ya bağlanır
                   ├── Arduino röleyi açar → anfi 220V alır → ses çalınır
                   └── RF kumandadan gelen sinyalleri Arduino alır → tarayıcıya iletir
```

**Kısaca:** Bilgisayar + Python sunucu + Chrome tarayıcı + Arduino = tam otomatik zil sistemi.

- **Python sunucu** (`zunucu/sunucu.py`): ses dosyalarını ve API'yi tarayıcıya sunar.
- **Chrome tarayıcı**: zil programını çalıştırır, saatleri kontrol eder, sesi çalar.
- **Arduino Uno**: USB üzerinden tarayıcıya bağlıdır. Anfi rölesini açıp kapar. RF kumanda sinyallerini alır.
- DİKKAT: Orjinal Arduino Uno kullanın. Klon çipli olan arduino unolar seri port bağlantısında sürekli sorun çıkarıyor. 
- **RF Kumanda (433 MHz, 4 kanal)**: kablosuz olarak İstiklâl Marşı, zil, anfi toggle ve durdur komutları gönderir.

---

## 📦 Gereksinimler

### Yazılım

| Yazılım | Sürüm | Nereden İndirilir |
|---------|-------|-------------------|
| **Python** | 3.10 veya üzeri | [python.org](https://www.python.org/downloads/) |
| **Google Chrome** | Güncel sürüm | [chrome.google.com](https://www.google.com/chrome/) |
| **Arduino IDE** | 2.x | [arduino.cc](https://www.arduino.cc/en/software) |

> ⚠️ Python kurulumunda **"Add Python to PATH"** kutucuğunu işaretlemeyi unutmayın!

### Donanım

| Parça | Adet | Açıklama |
|-------|------|----------|
| Arduino Uno | 1 | Röle ve RF kumanda kontrolü için |
| 5V Röle Modülü (30A) | 1 | Anfi 220V besleme kontrolü |
| RF 433MHz 4 Kanallı Alıcı | 1 | Uzaktan kumanda sinyali almak için |
| RF 433MHz 4 Kanallı Verici (kumanda) | 1 | Elle zil/marş başlatmak için |
| Çift Renkli LED (ortak katot) | 1 | Anfi durumu göstergesi |
| Direnç 100Ω | 1 | Yeşil LED için |
| Direnç 150Ω | 1 | Kırmızı LED için |
| Buton | 1 | Manuel anfi açma/kapama |
| USB Kablo (A-B, Arduino kablosu) | 1 | Arduino'yu bilgisayara bağlamak için |
| Bilgisayar (Windows 10/11) | 1 | Sistemi çalıştırmak için |

---

## 🚀 Kurulum (Adım Adım)

### 1. Dosyaları İndirin ve Yerleştirin

1. Bu repodaki tüm dosyaları indirin (ZIP olarak indirip çıkartın **veya** `git clone` yapın).
2. Çıkartılan `zil/` klasörünü istediğiniz bir yere koyun. Örnek: `C:\ZilSistemi\`
3. Klasörün içinde şunlar olmalı:
   - `zil-baslat.bat`
   - `zil.html`
   - `zunucu/` klasörü
   - `zilsesleri/` klasörü (mp3 dosyaları burada)

### 2. Python'un Kurulu Olduğunu Doğrulayın

Başlat menüsünü açın → `cmd` yazın → Enter'a basın → şunu yazın:

```
python --version
```

`Python 3.x.x` gibi bir çıktı görüyorsanız hazırsınız. Hata alıyorsanız Python'u kurun (yukarıdaki linkten).

### 3. Arduino Kodunu Yükleyin

1. **Arduino IDE**'yi açın.
2. `zil/anfi/anfi.ino` dosyasını açın (`Dosya → Aç`).
3. Arduino Uno'yu USB ile bilgisayara bağlayın.
4. Arduino IDE'de `Araçlar → Port` menüsünden Arduino'nun bağlı olduğu COM portunu seçin (örn. `COM3`).
5. `Araçlar → Kart` menüsünden `Arduino Uno`'yu seçin.
6. **Yükle** butonuna (→ oku) tıklayın. Yükleme tamamlanana kadar bekleyin.

### 4. Arduino'yu Devreye Bağlayın

Bağlantı şeması için [Arduino Bağlantı Şeması](#-arduino-bağlantı-şeması) bölümüne bakın.

### 5. Masaüstü Kısayolu Oluşturun (İsteğe Bağlı)

1. `zil-baslat.bat` dosyasına sağ tıklayın.
2. `Kısayol Oluştur` seçin.
3. Oluşan kısayolu masaüstüne taşıyın.
4. Kısayola sağ tıklayıp `Özellikler → Gelişmiş → Yönetici Olarak Çalıştır`'ı işaretleyin (firewall kuralı eklemek için gerekli).

---

## 📁 Klasör Yapısı

```
zil/
├── zil-baslat.bat          ← Sistemi başlatan dosya — ÇİFT TIKLA
├── zil.html                ← Ana kontrol paneli (Chrome'da açılır)
├── zil-port.txt            ← Sunucunun kullandığı port (otomatik oluşur)
├── zil-anons-ayar.json     ← Anons ses ayarları (otomatik kaydedilir)
├── blacklist.json          ← Devre dışı ses dosyaları listesi (otomatik)
│
├── anfi/
│   └── anfi.ino            ← Arduino kodu (bir kez yükle, hep çalışır)
│
├── zilsesleri/             ← TÜM SES DOSYALARI BURAYA GELECEK
│   ├── zil.mp3              ← Genel zil (manuel buton / RF kumanda)
│   ├── zil_tenefus.mp3      ← Tenefüs çıkışı / son zil (gün sonu)
│   ├── zil_ogrenci.mp3      ← Öğrenci girişi zili
│   ├── zil_ogretmen.mp3     ← Öğretmen girişi zili
│   ├── zil_toplanma.mp3     ← Sabah toplanma zili
│   ├── IstiklalMarsi.mp3    ← İstiklâl Marşı
│   ├── saygi1.mp3           ← Saygı duruşu (1 dakika)
│   ├── saygi2.mp3           ← Saygı duruşu (2 dakika)
│   ├── depremikaz.mp3       ← Deprem ikaz sesi
│   ├── siren.mp3            ← Deprem tahliye sireni
│   ├── anons_tenefus.mp3    ← Tenefüs çıkışı anonsu (zil sonrası)
│   ├── anons_toplanma.mp3   ← Toplanma anonsu (zil sonrası)
│   ├── anons_ogretmen.mp3   ← Öğretmen girişi anonsu (zil sonrası)
│   ├── anons_ogrenci.mp3    ← Öğrenci girişi anonsu (zil sonrası)
│   └── anons_gunsonu.mp3    ← Son zil / gün sonu anonsu
│
├── temp/                   ← Geçici olarak devre dışı bırakılan sesler
│
└── zunucu/                 ← Python sunucu dosyaları (dokunmayın)
    ├── sunucu.py
    ├── handler.py
    ├── utils.py
    ├── ezan.py
    └── zilsesler.py
```

---

## ▶️ Programı Başlatma

1. `zil-baslat.bat` dosyasına **çift tıklayın** (veya masaüstü kısayoluna).
2. Kısa bir süre siyah bir konsol penceresi görürsünüz — bu normaldir, küçültülmüş kalır.
3. Birkaç saniye içinde Chrome tarayıcı tam ekran açılır ve zil programı **otomatik olarak ön plana** gelir.
4. Program açıldıktan sonra **ilk kez herhangi bir yere tıklayın** — bu, tarayıcının ses çalma iznini etkinleştirir.

> 💡 Programı kapatmak için: Arayüzün sağ üstündeki **Sistemi Kapat** butonunu kullanın. Doğrudan Chrome'u kapatırsanız Python sunucu arka planda çalışmaya devam edebilir; bir sonraki açılışta otomatik kapatılır.

---

## 🖥️ Web Arayüzü — Sekme Sekme Açıklama

### Ana Ekran (Sol Panel)

Programı açtığınızda sol tarafta sabit bir kontrol paneli görürsünüz:

- **Saat**: Bilgisayarın güncel saati (büyük rakamlarla).
- **Sonraki Zil**: Bir sonraki zilin kaç dakika sonra çalacağı.
- **🔔 Zil / 🎖 Marş / 🤲 Saygı / ⚠️ İkaz** butonları: Elle istediğiniz sesi çalabilirsiniz.
- **⏹ Durdur**: Çalan sesi anında keser.
- **🔉 Anfi**: Anfi açma/kapama durumunu gösterir ve manuel kontrol sağlar.

### ⚙ Zil & Okul Sekmesi

Zil saatlerini ve okul ayarlarını buradan yaparsınız.

- **Ders sayısı**: Günlük kaç ders olduğunu girin (1–10).
- **Ders süresi**: Her dersin kaç dakika sürdüğünü girin.
- **Tenefüs süreleri**: Her tenefüsün kaç dakika olduğunu tek tek ayarlayın.
- **İlk ders başlangıcı**: İlk dersin başladığı saati girin (örn. 08:00).
- **Öğle arasını düzenle**: Öğle tatil başlangıcını ve bitişini ayarlayın.
- **Gün seçimi**: Pazartesi–Cuma için ayrı ayrı ayar yapılabilir.
- **Hafta sonu**: Cumartesi/Pazar zil çalmasını etkinleştirmek için işaretleyin.

Her değişikliği yaptıktan sonra **Kaydet** butonuna basın.

### 🔊 Ses Sekmesi

- Ses dosyalarının yüklü olup olmadığını gösterir. **Zil sesleri artık tek bir ortak sesle sınırlı değildir** — Tenefüs, Öğrenci, Öğretmen ve Toplanma zilleri için ayrı ayrı dosya tanımlanabilir (`zil_tenefus.mp3`, `zil_ogrenci.mp3`, `zil_ogretmen.mp3`, `zil_toplanma.mp3`), ayrıca Marş/Saygı/Deprem sesleri de buradadır.
- Her kutucuğun yanındaki 📁 butonuyla dosya seçtiğinizde, seçim **anında ve kalıcı olarak** `zilsesleri/` klasörüne kaydedilir — ayrıca bir "Kaydet" tuşuna basmanıza gerek yoktur, bilgisayar kapanıp açılsa da seçim kaybolmaz. (Bu otomatik kayıt yalnızca program yerel sunucu üzerinden — `zil-baslat.bat` ile — çalışırken geçerlidir.)
- **Ses kanalı seçimi**: Bilgisayarda birden fazla ses çıkışı varsa (örn. HDMI + kulaklık) hangi kanaldan ses çıkacağını seçin.
- **Ana ses seviyesi**: Genel ses yüksekliğini ayarlayın.
- Her ses için ▶ butonu ile test çalması yapabilirsiniz.
- **Zil Sonrası Anons Ayarları**: Her zil tipinden (Tenefüs, Öğretmen, Öğrenci, Toplanma, Son Zil) hemen sonra hangi anons dosyasının otomatik çalacağını belirleyin. Dropdown'dan seçim yapmanız yeterli — değişiklik anında kaydedilir, ayrıca "Kaydet" tuşuna basmaya gerek yoktur. *— Anons yok —* seçiliyse sadece zil çalar, anons çalmaz.

### 🎵 MP3 Zil Sekmesi

Tenefüs zili olarak standart zil.mp3 yerine kendi MP3 müziklerinizi çalabilirsiniz.

1. `zilsesleri/` klasörü içinde alt klasörler oluşturun (örn. `zilsesleri/muzik/`).
2. MP3 dosyalarınızı o klasöre koyun.
3. Bu sekmede ilgili klasörü seçin ve modu etkinleştirin.

### 🔉 Anfi Sekmesi

Arduino üzerinden anfi kontrolünü buradan yönetirsiniz.

- **🔌 Yeni Port**: İlk kurulumda tıklayın. Chrome bir USB cihaz listesi açar, Arduino'yu seçin. Seçim hatırlanır, bir daha sormaz.
- **Anfi Öncesi Gecikme**: Zil çalmadan kaç saniye önce anfi açılsın? (Anfi ısınma süresi için)
- **Anfi Sonrası Gecikme**: Zil bittikten kaç saniye sonra anfi kapansın?
- **Durum göstergesi**: Yeşil = Anfi açık, Kırmızı = Anfi kapalı.

### 🕌 Ezan Sekmesi

- Ezan vakitlerinde otomatik zil çalmayı durdurmak için kullanılır.
- İlçenizi seçin, Diyanet API'sinden vakit bilgisi otomatik çekilir.
- Ezan süresi boyunca zil çalmaz, ezan bittikten sonra devam eder.

### 📋 Manifest Sekmesi

Teknik bilgiler, versiyon geçmişi ve sistem mimarisi burada bulunur. Geliştirici referans belgesidir, normal kullanımda gerek yoktur.

---

## 📅 Zil Planları (A / B / C)

Sistem üç farklı zil planını destekler. Aynı gün için iki farklı program uygulamak gerektiğinde (örn. sınav günü) kullanılır.

| Plan | Ne Zaman Kullanılır? |
|------|----------------------|
| **Plan A** | Normal okul günü (varsayılan) |
| **Plan B** | Kısa gün, sınav günü veya özel program |
| **Plan C** | İkinci özel durum programı |

Her gün için hangi planın aktif olduğunu **Zil & Okul** sekmesinden seçebilirsiniz. Değişiklik anında kaydedilir.

---

## 🔉 Anfi (Amplifikatör) Kontrolü

Sistem, anfiyi her zil çalmadan önce otomatik olarak açar ve zil bittikten sonra kapatır. Bu sayede anfi sürekli açık kalmaz, enerji tasarrufu sağlanır.

**İlk Kurulum:**
1. Arduino'yu USB ile bilgisayara bağlayın.
2. Zil programını başlatın.
3. **Anfi** sekmesine gidin → **🔌 Yeni Port** butonuna tıklayın.
4. Açılan pencerede Arduino'yu seçin ve **Bağlan**'a tıklayın.
5. "Arduino otomatik bağlandı" mesajı görünürse başarılı.

**Sonraki Açılışlarda:** Arduino bağlı olduğu sürece sistem otomatik olarak tanır ve bağlanır, el ile bir şey yapmanıza gerek yoktur.

---

## 🔌 Arduino Bağlantı Şeması

```
Arduino Uno
├── Pin 7  ──── Röle IN (anfi 220V kontrolü)
├── Pin 11 ──[100Ω]──── Yeşil LED + (anfi açık göstergesi)
├── Pin 12 ──[150Ω]──── Kırmızı LED + (anfi kapalı göstergesi)
├── Pin 4  ──── Buton (diğer ucu GND — manuel anfi aç/kapat)
│
├── Pin 2  ──── RF Alıcı CH1-A (İstiklâl Marşı)
├── Pin 3  ──── RF Alıcı CH2-A (Zil çal)
├── Pin 5  ──── RF Alıcı CH3-A (Anfi aç/kapat)
├── Pin 6  ──── RF Alıcı CH4-A (Her şeyi durdur)
│
├── 5V     ──── Röle VCC
│               RF Alıcı VCC (5V veya 12V — modele göre)
└── GND    ──── Röle GND, LED(-), Buton, RF Alıcı tüm CH-B(COM), LED ortak katot
```

**Röle Bağlantısı (Anfi Tarafı):**
```
220V Şebeke ──[SİGORTA]──── Röle COM
                             Röle NO ──── Anfi 220V girişi
                             (Anfi açıldığında NO-COM kısa devre olur)
```

> ⚠️ 220V ile çalışırken mutlaka **yetkili bir elektrikçiye** yaptırın!

---

## 📡 RF Uzaktan Kumanda

433 MHz 4 kanallı RF kumanda ile sınıf dışından sistemi kontrol edebilirsiniz.

| Kumanda Tuşu | Fonksiyon |
|--------------|-----------|
| **A (CH1)** | 🎖 İstiklâl Marşı çal |
| **B (CH2)** | 🔔 Zil çal |
| **C (CH3)** | 🔉 Anfi aç / kapat (toggle) |
| **D (CH4)** | ⏹ Her şeyi durdur |

**Kumanda Menzili:** Açık alanda ~30–50 metre, duvarlar arasında ~10–20 metre.

**RF Alıcı Bağlantısı:**
- Her kanalın **A (NO)** çıkışı → ilgili Arduino pinine (2, 3, 5, 6)
- Her kanalın **B (COM)** çıkışı → Arduino GND
- Dahili pull-up direnci kullanıldığı için harici direnç **gerekmez**

---

## 🎵 Ses Dosyaları

Tüm ses dosyaları `zilsesleri/` klasöründe bulunmalıdır. Sistem açılışta bu klasörü tarar ve dosyaları otomatik yükler.

| Dosya Adı | Açıklama | Kullanıldığı Yer |
|-----------|----------|------------------|
| `zil.mp3` | Genel zil | Manuel "🔔 Zil" butonu, RF kumanda |
| `zil_tenefus.mp3` | Tenefüs/son zil sesi | Ders bitişi, gün sonu zili |
| `zil_ogrenci.mp3` | Öğrenci girişi zili | Tenefüs sonu (öğrenci girişi) |
| `zil_ogretmen.mp3` | Öğretmen girişi zili | Ders başlangıcı (öğretmen girişi) |
| `zil_toplanma.mp3` | Sabah toplanma zili | Toplanma saati |
| `IstiklalMarsi.mp3` | İstiklâl Marşı | Tören, RF-A tuşu |
| `saygi1.mp3` | Saygı duruşu (1 dk) | Tören öncesi |
| `saygi2.mp3` | Saygı duruşu (2 dk) | Tören öncesi |
| `depremikaz.mp3` | Deprem ikaz tonu | Deprem tatbikatı |
| `siren.mp3` | Tahliye sireni | Deprem tatbikatı |
| `anons_tenefus.mp3` | Tenefüs çıkışı anonsu | Zil sonrası (Ses → Anons ayarı) |
| `anons_toplanma.mp3` | Toplanma anonsu | Zil sonrası (Ses → Anons ayarı) |
| `anons_ogretmen.mp3` | Öğretmen girişi anonsu | Zil sonrası (Ses → Anons ayarı) |
| `anons_ogrenci.mp3` | Öğrenci girişi anonsu | Zil sonrası (Ses → Anons ayarı) |
| `anons_gunsonu.mp3` | Son zil / gün sonu anonsu | Zil sonrası (Ses → Anons ayarı) |

**Kendi Ses Dosyanızı Eklemek:**
- MP3 formatında olmalı.
- **Yöntem 1 (önerilen):** Ses sekmesinde ilgili kutucuğun 📁 butonuna tıklayıp dosyayı seçin — sistem otomatik olarak doğru adla (örn. `zil_ogrenci.mp3`) `zilsesleri/` klasörüne kalıcı kaydeder, ek bir işlem gerekmez.
- **Yöntem 2 (manuel):** Dosyayı doğru adla `zilsesleri/` klasörüne kendiniz kopyalayın, ardından programı yeniden başlatın (veya sayfayı F5 ile yenileyin). Dosya adı bu sayfadaki tabloyla **birebir eşleşmelidir** (`zil_ogrenci.mp3` gibi), aksi halde sistem dosyayı tanıyamaz.

---

## 🚨 Deprem Tatbikatı Modu

Ana ekrandaki **⚠️ İkaz** ve **🚨 Siren** butonları deprem tatbikatı için kullanılır.

- **İkaz**: `depremikaz.mp3` dosyasını tekrar tekrar çalar (tatbikat başladı sinyali).
- **Siren (Tahliye)**: `siren.mp3` dosyasını çalar (tahliye başladı sinyali).
- Her iki mod için çalma süresi ve tekrar sayısı arayüzden ayarlanabilir.
- **⏹ Durdur** butonu ile tatbikat anında sonlandırılır.

---

## 🕌 Ezan Entegrasyonu

- **Zil & Okul** sekmesinden ezan özelliğini etkinleştirin.
- İlçenizi seçin — Diyanet İşleri Başkanlığı API'sinden günlük vakit bilgisi otomatik alınır.
- Ezan vakitlerinde zil çalmaz. Ezan süresi dolunca normal programa devam eder.
- İnternet bağlantısı yoksa bu özellik devre dışı kalır, program normal çalışmaya devam eder.

---

## ❓ Sık Sorulan Sorular

**S: Programı her gün manuel başlatmak zorunda mıyım?**
C: Windows Görev Zamanlayıcısı ile `zil-baslat.bat` dosyasını her gün sabah belirli bir saatte otomatik başlatabilirsiniz. Görev Zamanlayıcısı → Görev Oluştur → Tetikleyici: Her gün saat 07:30 → Eylem: `zil-baslat.bat`.

**S: Zil saatlerini değiştirdim ama etki etmedi?**
C: **Kaydet** butonuna bastığınızdan emin olun. Kaydetmeden sekmeden ayrılırsanız değişiklikler kaybolur.

**S: Arduino bağlı ama anfi çalışmıyor?**
C: Anfi sekmesine gidin, bağlantı durumunu kontrol edin. "Bağlı değil" yazıyorsa **🔌 Yeni Port** butonuyla tekrar bağlanın.

**S: Ses çıkmıyor?**
C: (1) Bilgisayar sesinin açık olduğundan emin olun. (2) Ses sekmesinde doğru ses kanalının seçili olduğunu kontrol edin. (3) Arayüzde herhangi bir yere tıklayın (tarayıcı ses iznini etkinleştirmek için bir kez tıklama gerektirir).

**S: "Python bulunamadı" hatası alıyorum?**
C: Python kurulu değil veya PATH'e eklenmemiş. Python'u [python.org](https://www.python.org/downloads/)'dan indirin, kurulum sırasında **"Add Python to PATH"** seçeneğini işaretleyin.

**S: Chrome açılıyor ama sayfa gelmiyor?**
C: Python sunucusunun başlaması birkaç saniye alır. 15 saniye bekleyin. Hâlâ açılmıyorsa BAT penceresinde hata mesajı var mı kontrol edin.

**S: Ağdaki başka bir bilgisayardan kumanda edebilir miyim?**
C: Evet. `http://[sunucu-ip]:[port]/kumanda` adresine gidin (örn. `http://192.168.1.10:8765/kumanda`). Basit bir kumanda paneli açılır.

**S: Tenefüs, öğrenci ve öğretmen zilleri için ayrı ses tanımladım ama hâlâ eski zil çalıyor?**
C: Dosya adının tabloyla birebir eşleştiğinden emin olun (`zil_ogrenci.mp3`, `zil_ogretmen.mp3`, `zil_tenefus.mp3`, `zil_toplanma.mp3`). Ses sekmesinden 📁 ile yüklediyseniz otomatik kaydedilir; klasöre elle kopyaladıysanız sayfayı F5 ile yenilemeniz gerekir.

**S: Hakkında panelindeki telefon numarasına tıklayınca ne oluyor?**
C: WhatsApp sohbeti açılır (bilgisayarda WhatsApp masaüstü uygulaması kuruluysa onu, değilse WhatsApp Web'i açar). Sadece numarayı kopyalamak isterseniz yanındaki 📋 butonunu kullanın.

---

## 🔧 Sorun Giderme

### Siyah Konsol Ekranı Açılıp Kapanıyor

`zil-baslat.bat` dosyasına sağ tıklayın → **Yönetici Olarak Çalıştır**. Firewall kuralı ekleme yetkisi gerekiyor.

### "Port Bulunamadı" veya Sunucu 15 Saniyede Başlamadı

- Python kurulu mu? (`python --version` komutuyla kontrol edin)
- `zunucu/sunucu.py` dosyası mevcut mu?
- Antivirüs yazılımı Python'u engelliyor olabilir. Python.exe için istisna tanımlayın.

### COM Port Otomatik Bağlanmıyor

1. Arduino'nun USB kablosunun takılı olduğundan emin olun.
2. Anfi sekmesine gidin → **🔌 Yeni Port** butonuna tıklayın → listeden Arduino'yu seçin.
3. Arduino sürücüsü kurulu olmayabilir. Arduino IDE'yi kurmak sürücüleri de yükler.

### Kumandadan Ses Çalmıyor

- Program açıldıktan sonra **en az bir kez arayüze tıklayın**. Chrome güvenlik politikası gereği ilk tıklamaya kadar ses çalmaz.
- Ses dosyaları yüklü mü? Ses sekmesinde kontrol edin.

### Zil Çalmıyor

- Bilgisayar saatinin doğru olduğundan emin olun.
- Doğru gün planının seçili olduğunu kontrol edin (Plan A/B/C).
- O gün için ilgili zil satırında onay kutucuğunun işaretli olduğuna bakın.
- Ses sekmesinden ses dosyasının yüklü olduğunu doğrulayın.

---

## 🆕 Sürüm Notları

**Haziran 2026**
- Zil sesleri ayrıştırıldı: Tenefüs, Öğrenci, Öğretmen ve Toplanma zilleri artık kendi ses dosyalarını kullanabiliyor (`zil_tenefus.mp3`, `zil_ogrenci.mp3`, `zil_ogretmen.mp3`, `zil_toplanma.mp3`). Eski tek `zil.mp3` artık sadece manuel buton/RF kumanda için kullanılıyor.
- Tenefüs çıkışı için yeni anons desteği eklendi (`anons_tenefus.mp3`).
- Ses sekmesinden seçilen zil/anons dosyaları artık **otomatik ve kalıcı** olarak kaydediliyor — "Kaydet" tuşuna basmaya veya yeniden seçmeye gerek kalmadan, bilgisayar kapanıp açılsa bile ayar korunuyor.
- VU metre animasyonu, yan taraftaki ses kaydırıcılarını titretmeyecek şekilde yeniden yazıldı.
- Hakkında panelindeki telefon numarası artık tıklanınca doğrudan WhatsApp sohbeti açıyor.

---

## 👨‍💻 Geliştirici Bilgisi

- **Tasarım:** Mustafa Necati BOZOK
- **Kodlama:** Claude (Anthropic)
- **Lisans:** Eğitim amaçlı serbest kullanım
- **Son Güncelleme:** Haziran 2026

---

*Bu README, sistemi hiç görmemiş bir kullanıcının tüm adımları takip ederek kurulum yapabilmesi için hazırlanmıştır.*
