/*
 * Okul Zil Sistemi — Anfi Kontrol Arduino Kodu
 * Tasarim : Mustafa Necati BOZOK
 * Kodlama : Claude (Anthropic) - Haziran 2026
 * Kart    : Arduino Uno
 *
 * Baglantilar:
 *   Röle IN pini        → Arduino Digital Pin 7
 *   Röle VCC            → Arduino 5V
 *   Röle GND            → Arduino GND
 *   Buton               → Arduino Digital Pin 4  (diğer ucu GND'ye)
 *
 *   Çift Renkli LED (ortak katot):
 *   Kırmızı anot        → Arduino Digital Pin 12  (150Ω direnç üzerinden)
 *   Yeşil anot          → Arduino Digital Pin 11  (100Ω direnç üzerinden)
 *   Ortak katot         → Arduino GND
 *
 *   RF Alıcı 433MHz — 4 Kanal (anlık mod, dahili pull-up, harici direnç gerekmez):
 *   CH1 A(NO) → D2  : İstiklal Marşı
 *   CH2 A(NO) → D3  : Zil çal
 *   CH3 A(NO) → D5  : Anfi aç/kapat (toggle)
 *   CH4 A(NO) → D6  : DUR — her şeyi durdur
 *   Tüm CH x B(COM) → Arduino GND
 *
 * Seri port: 9600 baud
 * Komutlar : ANFI_AC  → Anfi aç  (röle kapanır, 220V akar)
 *            ANFI_KAP → Anfi kapat (röle açılır, 220V kesilir)
 *            DURUM    → Mevcut durumu sorgula
 * Mesajlar : MARS:TETIKLEME   → İstiklal Marşı çal
 *            ZIL:TETIKLEME    → Zil çal
 *            ANFI:TOGGLE      → Anfi aç/kapat
 *            DUR:TETIKLEME    → Her şeyi durdur
 */

const int ROLE_PIN    = 7;   // Röle sinyal pini
const int LED_KIRMIZI = 12;  // Çift renkli LED — kırmızı anot (anfi kapalı)
const int LED_YESIL   = 11;  // Çift renkli LED — yeşil anot  (anfi açık)
const int BUTON_PIN   = 4;   // Manuel buton pini (GND'ye bağlı, INPUT_PULLUP)

// RF Alıcı pinleri (hepsi INPUT_PULLUP — röle kapanınca LOW olur)
const int RF_MARS  = 2;   // CH1 — İstiklal Marşı
const int RF_ZIL   = 3;   // CH2 — Zil çal
const int RF_ANFI  = 5;   // CH3 — Anfi toggle
const int RF_DUR   = 6;   // CH4 — DUR

// Röle mantığı: Optokuplörlü modüllerde LOW = aktif (anfi açık)
// Eğer röleniz HIGH aktifse ROLE_ACIK ve ROLE_KAPALI degerlerini değiştirin
const int ROLE_ACIK   = LOW;  // Röle kapanır → 220V akar  → Anfi açılır
const int ROLE_KAPALI = HIGH;   // Röle açılır  → 220V kesilir → Anfi kapanır

// Buton debounce süresi (ms) — titreşimi önler
const unsigned long DEBOUNCE_MS = 50;

bool anfiDurum    = false;
String komutBuffer = "";

// Buton durum takibi
int  butonSon         = HIGH;
int  butonOnceki      = HIGH;
unsigned long butonZamani = 0;

// RF kanal durum takibi — her kanal için aynı yapı
struct RfKanal {
  int pin;
  int son;
  int onceki;
  unsigned long zamani;
  const char* mesaj;
};

RfKanal rfKanallar[] = {
  { RF_MARS, HIGH, HIGH, 0, "MARS:TETIKLEME" },
  { RF_ZIL,  HIGH, HIGH, 0, "ZIL:TETIKLEME"  },
  { RF_ANFI, HIGH, HIGH, 0, "ANFI:TOGGLE"    },
  { RF_DUR,  HIGH, HIGH, 0, "DUR:TETIKLEME"  },
};

void anfiAc() {
  digitalWrite(ROLE_PIN, ROLE_ACIK);
  anfiDurum = true;
  Serial.println("OK:ANFI_ACILDI");
}

void anfiKapat() {
  digitalWrite(ROLE_PIN, ROLE_KAPALI);
  anfiDurum = false;
  Serial.println("OK:ANFI_KAPATILDI");
}

void setup() {
  pinMode(ROLE_PIN, OUTPUT);
  
  // Boot titreşimlerini geçmesini bekle
  digitalWrite(ROLE_PIN, ROLE_KAPALI);  // Önce hemen kapat
  delay(500);                            // 500ms bekle
  digitalWrite(ROLE_PIN, ROLE_KAPALI);  // Tekrar kapat (güvenlik için)
  
  pinMode(LED_KIRMIZI, OUTPUT);
  pinMode(LED_YESIL,   OUTPUT);
  pinMode(BUTON_PIN, INPUT_PULLUP);

  // RF alıcı pinleri — dahili pull-up, röle açıkken HIGH'da bekler
  pinMode(RF_MARS, INPUT_PULLUP);
  pinMode(RF_ZIL,  INPUT_PULLUP);
  pinMode(RF_ANFI, INPUT_PULLUP);
  pinMode(RF_DUR,  INPUT_PULLUP);
  // Başlangıçta anfi kapalı → kırmızı yansın
  digitalWrite(LED_KIRMIZI, HIGH);
  digitalWrite(LED_YESIL,   LOW);

  Serial.begin(9600);
  Serial.println("ZIL_ARDUINO_HAZIR");
  Serial.println("Komutlar: ANFI_AC | ANFI_KAP | DURUM");
}

void loop() {

  /* ── 1. Seri porttan gelen komutları işle ─────────────────────── */
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      komutBuffer.trim();
      if (komutBuffer.length() > 0) {
        komutIsle(komutBuffer);
      }
      komutBuffer = "";
    } else {
      komutBuffer += c;
    }
  }

  /* ── 2. Manuel buton kontrolü (debounce ile) ──────────────────── */
  int butonSimdi = digitalRead(BUTON_PIN);

  // Pinден okunan değer değiştiyse debounce zamanlayıcısını sıfırla
  if (butonSimdi != butonSon) {
    butonZamani = millis();
    butonSon = butonSimdi;
  }

  // Debounce süresi geçti ve durum kararlı hale geldi
  if ((millis() - butonZamani) >= DEBOUNCE_MS) {
    // Kararlı durum öncekinden farklıysa işle
    if (butonSimdi != butonOnceki) {
      butonOnceki = butonSimdi;
      // Sadece basma anında (HIGH→LOW) tetikle
      if (butonSimdi == LOW) {
        Serial.println("BUTON:MANUEL_TETIKLEME");
        if (anfiDurum) {
          anfiKapat();
        } else {
          anfiAc();
        }
      }
    }
  }

  /* ── 3. RF kumanda kontrolü — 4 kanal (debounce ile) ────────── */
  int rfSayisi = sizeof(rfKanallar) / sizeof(rfKanallar[0]);
  for (int i = 0; i < rfSayisi; i++) {
    RfKanal& k = rfKanallar[i];
    int simdi = digitalRead(k.pin);
    if (simdi != k.son) {
      k.zamani = millis();
      k.son = simdi;
    }
    if ((millis() - k.zamani) >= DEBOUNCE_MS) {
      if (simdi != k.onceki) {
        k.onceki = simdi;
        if (simdi == LOW) {          // Düşen kenar — röle kapandı
          Serial.println(k.mesaj);
        }
      }
    }
  }

  /* ── 4. LED renk göstergesi (anfi açık → yeşil, kapalı → kırmızı) ─ */
  digitalWrite(LED_KIRMIZI, anfiDurum ? LOW  : HIGH);
  digitalWrite(LED_YESIL,   anfiDurum ? HIGH : LOW);
}

void komutIsle(String komut) {
  if (komut == "ANFI_AC") {
    anfiAc();

  } else if (komut == "ANFI_KAP") {
    anfiKapat();

  } else if (komut == "DURUM") {
    Serial.print("DURUM:");
    Serial.println(anfiDurum ? "ACIK" : "KAPALI");

  } else {
    Serial.print("HATA:BILINMEYEN_KOMUT:");
    Serial.println(komut);
  }
}
