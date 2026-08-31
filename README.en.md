> Last updated: September 1, 2026

[🇹🇷 Türkçe](README.md) | **🇬🇧 English**

# 🔔 School Bell System

An **Arduino-powered smart bell system** that automatically manages class periods, breaks, National Anthem ceremonies, and earthquake drills in schools. The program runs from a computer and connects to your existing amplifier/speaker system through the sound card. Bell times are configured easily from a web interface and can also be controlled remotely with an RF remote.

---

## 📋 Table of Contents

1. [How the System Works](#-how-the-system-works)
2. [Requirements](#-requirements)
3. [Installation (Step by Step)](#-installation-step-by-step)
4. [Folder Structure](#-folder-structure)
5. [Starting the Program](#️-starting-the-program)
6. [Web Interface — Tab by Tab](#️-web-interface--tab-by-tab)
7. [Bell Plans (A / B / C)](#-bell-plans-a--b--c)
8. [Amplifier Control](#-amplifier-control)
9. [Arduino Wiring Diagram](#-arduino-wiring-diagram)
10. [RF Remote Control](#-rf-remote-control)
11. [Sound Files](#-sound-files)
12. [Earthquake Drill Mode](#-earthquake-drill-mode)
13. [Prayer Time Integration](#-prayer-time-integration)
14. [FAQ](#-faq)
15. [Troubleshooting](#-troubleshooting)
16. [Release Notes](#-release-notes)

---

## 🧠 How the System Works

```
[zil-baslat.bat]
       │
       ├──▶ [Python Server] ──▶ serves files and the API over localhost:PORT
       │         │
       │         └──▶ writes the port number to zil-port.txt
       │
       └──▶ [Google Chrome] ──▶ http://localhost:PORT/zil.html
                   │
                   ├── Displays the bell schedule (browser = control panel)
                   ├── Connects to the Arduino over a serial (USB) port
                   ├── Arduino switches the relay → amplifier gets 220V → sound plays
                   └── Arduino receives RF remote signals → forwards them to the browser
```

**In short:** Computer + Python server + Chrome browser + Arduino = a fully automatic bell system.

- **Python server** (`zunucu/sunucu.py`): serves sound files and the API to the browser.
- **Chrome browser**: runs the bell schedule, tracks the clock, plays sound.
- **Arduino Uno**: connected to the browser over USB. Switches the amplifier relay on/off and receives RF remote signals.
- **RF Remote (433 MHz, 4-channel)**: wirelessly triggers the National Anthem, bell, amplifier toggle, and stop-all commands.
- <u>**NOTE:**</u> <span style="color:red"><u>Use a genuine Arduino Uno. Clone-chip Arduino Unos frequently cause serial-port connection issues.</u></span>

---

## 📦 Requirements

### Software

| Software | Version | Where to Download |
|---------|-------|-------------------|
| **Python** | 3.10 or higher | [python.org](https://www.python.org/downloads/) |
| **Google Chrome** | Latest version | [chrome.google.com](https://www.google.com/chrome/) |
| **Arduino IDE** | 2.x | [arduino.cc](https://www.arduino.cc/en/software) |

> ⚠️ Don't forget to check **"Add Python to PATH"** during Python installation!

### Hardware

| Part | Qty | Description |
|-------|------|----------|
| Arduino Uno | 1 | For relay and RF remote control |
| 5V Relay Module (30A) | 1 | Controls the amplifier's 220V supply |
| RF 433MHz 4-Channel Receiver | 1 | Receives remote control signals |
| RF 433MHz 4-Channel Transmitter (remote) | 1 | Manually triggers bell/anthem |
| Bi-color LED (common cathode) | 1 | Amplifier status indicator |
| 100Ω Resistor | 1 | For the green LED |
| 150Ω Resistor | 1 | For the red LED |
| Push Button | 1 | Manual amplifier on/off |
| USB Cable (A-B, Arduino cable) | 1 | Connects the Arduino to the computer |
| Computer (Windows 10/11) | 1 | Runs the system |

---

## 🚀 Installation (Step by Step)

### 1. Download and Place the Files

1. Download all files in this repo (as a ZIP and extract it, **or** `git clone`).
2. Put the extracted `zil/` folder wherever you like, e.g. `C:\ZilSistemi\`
3. The folder should contain:
   - `zil-baslat.bat`
   - `zil.html`
   - the `zunucu/` folder
   - the `zilsesleri/` folder (your mp3 files go here)

### 2. Verify Python Is Installed

Open the Start menu → type `cmd` → press Enter → type:

```
python --version
```

If you see something like `Python 3.x.x`, you're ready. If you get an error, install Python from the link above.

### 3. Upload the Arduino Sketch

1. Open **Arduino IDE**.
2. Open `zil/anfi/anfi.ino` (`File → Open`).
3. Connect the Arduino Uno to the computer via USB.
4. In Arduino IDE, select the COM port the Arduino is connected to from `Tools → Port` (e.g. `COM3`).
5. Select `Arduino Uno` from `Tools → Board`.
6. Click **Upload** (→ arrow icon). Wait until the upload finishes.

### 4. Wire the Arduino into the Circuit

See the [Arduino Wiring Diagram](#-arduino-wiring-diagram) section for the schematic.

### 5. Create a Desktop Shortcut (Optional)

1. Right-click `zil-baslat.bat`.
2. Select `Create shortcut`.
3. Move the shortcut to your desktop.
4. Right-click the shortcut → `Properties → Advanced → Run as administrator` (needed to add a firewall rule).

---

## 📁 Folder Structure

```
zil/
├── zil-baslat.bat          ← Launches the system — DOUBLE-CLICK
├── arduino-usb-fix.bat     ← Permanently fixes Arduino USB issues (run as admin once)
├── zil.html                ← Main control panel (opens in Chrome)
├── zil-port.txt            ← Port used by the server (created automatically)
├── zil-anons-ayar.json     ← Announcement sound settings (saved automatically)
├── zil-ses-ayar.json       ← Bell sound file selections (saved automatically)
├── blacklist.json          ← List of disabled sound files (automatic)
│
├── anfi/
│   └── anfi.ino            ← Arduino code (upload once, runs forever)
│
├── zilsesleri/             ← ALL SOUND FILES GO HERE
│   ├── zil.mp3              ← General bell + default for all bell types
│   ├── zil_tenefus.mp3      ← (optional) custom sound for break/last bell
│   ├── zil_ogrenci.mp3      ← (optional) custom sound for student entry
│   ├── zil_ogretmen.mp3     ← (optional) custom sound for teacher entry
│   ├── zil_toplanma.mp3     ← (optional) custom sound for morning assembly
│   ├── IstiklalMarsi.mp3    ← National Anthem
│   ├── saygi1.mp3           ← Moment of silence (1 minute)
│   ├── saygi2.mp3           ← Moment of silence (2 minutes)
│   ├── depremikaz.mp3       ← Earthquake alert tone
│   ├── siren.mp3            ← Earthquake evacuation siren
│   ├── anons_tenefus.mp3    ← Break-exit announcement (after the bell)
│   ├── anons_toplanma.mp3   ← Assembly announcement (after the bell)
│   ├── anons_ogretmen.mp3   ← Teacher-entry announcement (after the bell)
│   ├── anons_ogrenci.mp3    ← Student-entry announcement (after the bell)
│   └── anons_gunsonu.mp3    ← Last bell / end-of-day announcement
│
├── temp/                   ← Temporarily disabled sound files
│
└── zunucu/                 ← Python server files (don't touch)
    ├── sunucu.py
    ├── handler.py
    ├── utils.py
    ├── ezan.py
    └── zilsesler.py
```

---

## ▶️ Starting the Program

1. **Double-click** `zil-baslat.bat` (or its desktop shortcut).
2. You'll briefly see a black console window — this is normal, it stays minimized.
3. Within a few seconds, Chrome opens in full screen and the bell program **automatically comes to the foreground**.
4. Once the program opens, **click anywhere once** — this enables the browser's audio playback permission.

> 💡 To close the program, use the **Shut Down System** button in the top-right of the interface. If you close Chrome directly, the Python server may keep running in the background; it will be closed automatically the next time you start it.

---

## 🖥️ Web Interface — Tab by Tab

### Main Screen (Left Panel)

When you open the program, you'll see a fixed control panel on the left:

- **Clock**: The computer's current time, in large digits.
- **Next Bell**: How many minutes until the next bell.
- **🔔 Bell / 🎖 Anthem / 🤲 Tribute / ⚠️ Alert** buttons: manually play any of these sounds.
- **⏹ Stop**: instantly cuts off any playing sound.
- **🔉 Amp**: shows the amplifier's on/off status and provides manual control.

### 🏫 School / Language Tab

Configure school info and the interface language here.

- **School Name / Province-District**: shown in the top bar.
- **🌐 Dil / Language**: switches the interface between **Turkish** and **English**. Your chosen language is saved permanently in the browser — the program keeps using your last-chosen language even after the program or computer is restarted. If no language has ever been chosen (first launch), the program **always starts in Turkish**, regardless of the computer's/browser's operating-system language.

### 🔔 Bell Planning Tab

This is where you configure bell times. **Plan A / Plan B / Plan C now live in their own sub-tabs** — use the **Ⓐ Plan A · Ⓑ Plan B · Ⓒ Plan C** tabs at the top of the panel to jump straight to a plan's settings (and calendar, where applicable) with one click; only the selected plan's settings are shown at a time, so the three plans no longer blend together on one long page. Whichever plan is actually active is automatically selected whenever you open the panel.

- **Number of lessons**: enter how many lessons occur per day (1–10).
- **Lesson duration**: how many minutes each lesson lasts.
- **Break durations**: set the length of each break individually.
- **First lesson start time**: when the first lesson begins (e.g. 08:00).
- **Lunch break**: set the start and end of the lunch break.
- **Day selection**: Monday–Friday can each be configured separately.
- **Weekend**: check to enable the bell on Saturday/Sunday.
- **Friday Ceremony Mode**: when enabled, a chosen lesson runs shorter every Friday and rows after it are shown as inactive (dimmed) in the schedule, allowing an early exit for the ceremony.
- **Plan B / Plan C Calendar**: a weekly/date-based calendar that automatically switches to Plan B or Plan C on selected days or one-time dates.

Click **Save** after each change (most settings already auto-save instantly).

### 🔇 Quiet Mode Tab

Silences **all automatic bells** on selected days, weeks, or months (e.g. holidays, exam weeks).

- Pick a date from the calendar and add it as a **day / week / month** to the quiet-mode list.
- Automatic bells don't ring on quiet-mode days; **manual buttons (🔔 Bell, 🎖 Anthem, etc.) are unaffected** and can still be triggered by hand.
- Records can be removed individually or all at once with **🗑 Delete All**.

### 🔊 Bell Sound Files Tab

- Shows whether sound files are loaded. **Bell sounds are no longer limited to a single shared sound** — Break, Student, Teacher, and Assembly bells can each have their own file (`zil_tenefus.mp3`, `zil_ogrenci.mp3`, `zil_ogretmen.mp3`, `zil_toplanma.mp3`), and the Anthem/Tribute/Earthquake sounds are here too.
- When you pick a file with the 📁 button next to each slot, the selection is saved **instantly and permanently** to the `zilsesleri/` folder — no need to press a "Save" button, and the selection survives a computer restart. (This auto-save only applies while the program runs through the local server, i.e. via `zil-baslat.bat`.)
- **Main volume**: adjust the overall volume level. (Audio output channel selection now lives in the **⏻ Shutdown / Channel** tab.)
- Every sound has a ▶ button for a test playback.
- **Post-Bell Announcement Settings**: choose which announcement file plays automatically right after each bell type (Break, Teacher, Student, Assembly, Last Bell). Just pick from the dropdown — the change saves instantly, no "Save" button needed. If *— No announcement —* is selected, only the bell plays, no announcement.

### 🎵 MP3 Bell Tab

Instead of the standard zil.mp3, you can play your own MP3 tracks as the break bell.

1. Create subfolders inside `zilsesleri/` (e.g. `zilsesleri/muzik/`).
2. Put your MP3 files in that folder.
3. Select the folder in this tab and enable the mode.

### 🔉 Amplifier Tab

Manage amplifier control via Arduino from here.

- **🔌 New Port**: click this during first-time setup. Chrome opens a list of USB devices — select the Arduino. The choice is remembered afterward.
- **Pre-Bell Delay**: how many seconds before the bell the amplifier turns on (for amp warm-up time).
- **Post-Bell Delay**: how many seconds after the bell ends the amplifier turns off.
- **Status indicator**: Green = amp on, Red = amp off.

### 🕌 Prayer Times Tab

- Used to stop automatic bells during prayer times (toggled with the **🕌 Active** checkbox).
- **Before / After tolerance (min)**: instead of one shared "± min" tolerance, you can now set the time **before** a prayer and the time **after** a prayer separately (e.g. Before: 2min, After: 2min). Both default to **2 minutes**. A bell is treated as conflicting if it falls between "Before" minutes early and "After" minutes late relative to the prayer time.
- Once you pick a province/district, today's prayer times are fetched automatically. The system isn't tied to a single source — it tries Server Proxy → Diyanet, Diyanet (direct), diyanethaber.com.tr, Habertürk, NTV, and the Aladhan API in sequence, moving to the next source automatically if one fails. Manual time entry is also available.
- **Manual time edits now stick:** if you manually change a single prayer time in the Manual Time Entry boxes (e.g. correcting the Noon time), that value is used for **that day** going forward — even if the app re-fetches times afterward (via the 🕌 Fetch button or the daily auto-fetch), **your manual value is not overwritten**. Any other times you didn't touch keep updating automatically as usual. A manually-edited time is marked with a ✎ icon in the "Today's Prayer Times" list. Use **↺ Reset Today** to clear all of today's manual edits and go back to fully automatic times. (These edits are date-specific — the next day automatically uses freshly fetched times again.)
- While prayer mode is active, a conflicting bell **is automatically silenced** (does not ring) and a **"⚠️ Bell Could Not Ring!"** toast notification appears in the top corner of the screen.
- **Conflict warning in the bell table**: on the main schedule table, if a bell scheduled in a row conflicts with a prayer time, a red warning now appears right under that specific bell (e.g. *"Öğle Ezanı Saati. Ses Kapalı"* / "Noon Prayer Time. Sound Off") — so you can see ahead of time, right from the table, which bell won't ring and why. If more than one bell in the same row conflicts (e.g. Break Exit + Student Bell), each gets its own warning shown separately.

### ⏻ Shutdown / Channel Tab

- **Auto Shutdown**: safely shuts the computer down at a time you specify (an amp-off signal is sent first, then the server issues a `shutdown` command a few seconds later). Only works while the program runs through the local server (`zil-baslat.bat`).
- **Audio Output Channel**: if the computer has more than one audio output (e.g. HDMI + headphones), choose which one plays sound here, rescan devices with **🔄 Scan**, and make your selection permanent with **💾 Save**.

### 📋 Manifest Tab

Technical information, version history, and system architecture live here. It's a developer reference document and isn't needed for normal use.

---

## 📅 Bell Plans (A / B / C)

The system supports three different bell plans, used when the same day needs two different schedules (e.g. an exam day).

| Plan | When to Use |
|------|----------------------|
| **Plan A** | Normal school day (default) |
| **Plan B** | Short day, exam day, or a special schedule |
| **Plan C** | Block-lesson schedule (lessons are merged in pairs/groups, no bell rings between them) |

You can choose which plan is active for each day from the **Bell & School** tab. Changes save instantly.

---

## 🔉 Amplifier Control

The system automatically turns the amplifier on before every bell and off after it finishes, so the amp isn't left running continuously, saving energy.

**First-Time Setup:**
1. Connect the Arduino to the computer via USB.
2. Start the bell program.
3. Go to the **Amp** tab → click **🔌 New Port**.
4. In the dialog that opens, select the Arduino and click **Connect**.
5. If you see "Arduino auto-connected," it worked.

**On Subsequent Startups:** as long as the Arduino is connected, the system recognizes and connects to it automatically — no manual action needed.

---

## 🔌 Arduino Wiring Diagram

```
Arduino Uno
├── Pin 7  ──── Relay IN (controls amp's 220V)
├── Pin 11 ──[100Ω]──── Green LED + (amp-on indicator)
├── Pin 12 ──[150Ω]──── Red LED + (amp-off indicator)
├── Pin 4  ──── Button (other leg to GND — manual amp on/off)
│
├── Pin 2  ──── RF Receiver CH1-A (National Anthem)
├── Pin 3  ──── RF Receiver CH2-A (Play bell)
├── Pin 5  ──── RF Receiver CH3-A (Amp on/off)
├── Pin 6  ──── RF Receiver CH4-A (Stop everything)
│
├── 5V     ──── Relay VCC
│               RF Receiver VCC (5V or 12V — depends on model)
└── GND    ──── Relay GND, LED(-), Button, RF Receiver all CH-B (COM), LED common cathode
```

**Relay Wiring (Amplifier Side):**
```
220V Mains ──[FUSE]──── Relay COM
                         Relay NO ──── Amp's 220V input
                         (NO-COM short when the amp is switched on)
```

> ⚠️ Always have a **licensed electrician** handle the 220V wiring!

---

## 📡 RF Remote Control

Control the system from outside the classroom with a 433 MHz 4-channel RF remote.

| Remote Button | Function |
|--------------|-----------|
| **A (CH1)** | 🎖 Play National Anthem |
| **B (CH2)** | 🔔 Play bell |
| **C (CH3)** | 🔉 Amp on / off (toggle) |
| **D (CH4)** | ⏹ Stop everything |

**Remote Range:** ~30–50 meters in open areas, ~10–20 meters through walls.

**RF Receiver Wiring:**
- Each channel's **A (NO)** output → the corresponding Arduino pin (2, 3, 5, 6)
- Each channel's **B (COM)** output → Arduino GND
- Since internal pull-up resistors are used, an external resistor is **not needed**

---

## 🎵 Sound Files

All sound files must be placed in the `zilsesleri/` folder. The system scans this folder and loads the files automatically at startup.

> 💡 **Default sound:** all bell types (Break, Student, Teacher, Assembly) play `zil.mp3` by default. Uploading a custom file is **optional** — pick a different MP3 with 📁 and that bell type plays its own sound while the rest keep using `zil.mp3`. In the settings panel, bell types still using the default (zil.mp3) show in orange; ones with a custom file show in green.

| File Name | Description | Used For |
|-----------|----------|------------------|
| `zil.mp3` | General bell | Manual "🔔 Bell" button, RF remote |
| `zil_tenefus.mp3` | Break/last bell sound | End of lesson, end-of-day bell |
| `zil_ogrenci.mp3` | Student entry bell | End of break (student entry) |
| `zil_ogretmen.mp3` | Teacher entry bell | Start of lesson (teacher entry) |
| `zil_toplanma.mp3` | Morning assembly bell | Assembly time |
| `IstiklalMarsi.mp3` | National Anthem | Ceremony, RF button A |
| `saygi1.mp3` | Moment of silence (1 min) | Before ceremony |
| `saygi2.mp3` | Moment of silence (2 min) | Before ceremony |
| `depremikaz.mp3` | Earthquake alert tone | Earthquake drill |
| `siren.mp3` | Evacuation siren | Earthquake drill |
| `anons_tenefus.mp3` | Break-exit announcement | After the bell (Sound → Announcement setting) |
| `anons_toplanma.mp3` | Assembly announcement | After the bell (Sound → Announcement setting) |
| `anons_ogretmen.mp3` | Teacher-entry announcement | After the bell (Sound → Announcement setting) |
| `anons_ogrenci.mp3` | Student-entry announcement | After the bell (Sound → Announcement setting) |
| `anons_gunsonu.mp3` | Last bell / end-of-day announcement | After the bell (Sound → Announcement setting) |

**Adding Your Own Sound File:**
- Must be in MP3 format.
- **Method 1 (recommended):** click the 📁 button next to the relevant slot in the Sound tab and pick the file — the system automatically saves it under the correct name (e.g. `zil_ogrenci.mp3`) to the `zilsesleri/` folder, no extra steps needed.
- **Method 2 (manual):** copy the file yourself into `zilsesleri/` under the exact right name, then restart the program (or refresh the page with F5). The filename must **exactly match** the table above (e.g. `zil_ogrenci.mp3`), or the system won't recognize it.

---

## 🚨 Earthquake Drill Mode

The **⚠️ Alert** and **🚨 Siren** buttons on the main screen are used for earthquake drills.

- **Alert**: repeatedly plays `depremikaz.mp3` (signals the drill has started).
- **Siren (Evacuate)**: plays `siren.mp3` (signals evacuation has started).
- Playback duration and repeat count for both modes are configurable from the interface.
- The **⏹ Stop** button ends the drill instantly at any point.

---

## 🕌 Prayer Time Integration

- Enable the prayer-time feature from the **Bell & School** tab.
- Select your district — daily prayer times are fetched automatically from the Diyanet (Turkish Presidency of Religious Affairs) API.
- The bell doesn't ring during prayer times and resumes the normal schedule once the window ends.
- Without an internet connection, this feature is simply disabled and the program keeps running normally.

---

## ❓ FAQ

**Q: Do I have to start the program manually every day?**
A: Yes, unless you use Windows Task Scheduler to launch `zil-baslat.bat` automatically at a set time each morning. Task Scheduler → Create Task → Trigger: Daily at 07:30 → Action: `zil-baslat.bat`.

**Q: I changed the bell times but nothing happened?**
A: Make sure you pressed **Save**. If you leave the tab without saving, your changes are lost.

**Q: The Arduino is connected but the amp isn't working?**
A: Go to the Amp tab and check the connection status. If it says "Not connected," reconnect with the **🔌 New Port** button.

**Q: No sound is coming out?**
A: (1) Make sure the computer's volume is turned up. (2) Check that the right audio channel is selected in the Sound tab. (3) Click anywhere in the interface (Chrome requires one click before it allows audio playback).

**Q: I'm getting a "Python not found" error?**
A: Python isn't installed or isn't in the PATH. Download Python from [python.org](https://www.python.org/downloads/) and check **"Add Python to PATH"** during installation.

**Q: Chrome opens but the page doesn't load?**
A: The Python server takes a few seconds to start. Wait 15 seconds. If it still doesn't load, check the BAT window for an error message.

**Q: Can I control it from another computer on the network?**
A: Yes. Go to `http://[server-ip]:[port]/kumanda` (e.g. `http://192.168.1.10:8765/kumanda`). A simple remote-control panel opens.

**Q: I set separate sounds for break, student, and teacher bells, but the old bell still plays?**
A: Make sure the filename matches the table exactly (`zil_ogrenci.mp3`, `zil_ogretmen.mp3`, `zil_tenefus.mp3`, `zil_toplanma.mp3`). If you uploaded it via the Sound tab's 📁 button it saves automatically; if you copied it manually into the folder, refresh the page with F5.

**Q: What happens when I click the phone number in the About panel?**
A: It opens a WhatsApp chat (using the WhatsApp desktop app if installed, otherwise WhatsApp Web). If you just want to copy the number, use the 📋 button next to it.

---

## 🔧 Troubleshooting

### A Black Console Window Opens and Closes

Right-click `zil-baslat.bat` → **Run as administrator**. Adding a firewall rule requires elevated permissions.

### "Port Not Found" or the Server Doesn't Start Within 15 Seconds

- Is Python installed? (check with `python --version`)
- Does `zunucu/sunucu.py` exist?
- Antivirus software might be blocking Python. Add an exception for python.exe.

### COM Port Doesn't Auto-Connect

1. Make sure the Arduino's USB cable is plugged in.
2. Go to the Amp tab → click **🔌 New Port** → select the Arduino from the list.
3. The Arduino driver might not be installed. Installing the Arduino IDE also installs the drivers.
4. **For USB connection issues:** right-click `arduino-usb-fix.bat` and run it once as **administrator**. It disables Windows' USB power management so the computer no longer puts the Arduino to sleep. If the issue recurs, unplug and replug the Arduino — the program reconnects automatically.

### The Remote Doesn't Play Sound

- **Click anywhere in the interface at least once** after the program opens. Chrome's security policy blocks audio playback until the first click.
- Are the sound files loaded? Check the Sound tab.

### The Bell Doesn't Ring

- Make sure the computer's clock is correct.
- Check that the right day plan is selected (Plan A/B/C).
- Confirm the checkbox for that bell's row is checked for that day.
- Verify the sound file is loaded in the Sound tab.

---

## 🆕 Release Notes

**September 1, 2026 (4)**
- **Fixed a repeated-word label like "10. Lesson Lesson End":** the top-right "Next Bell" box and the activity log tagged the lesson-end bell by taking the lesson's name ("10. Lesson" — which already contains the word "Lesson") and appending "Lesson End" to it, producing a confusing repetition like "10. Lesson Lesson End". There was nothing wrong with the time itself — 17:25 really is when lesson 10 ends — the issue was purely in the wording. It now reads "10. Lesson **Finished**", without the repetition.

**September 1, 2026 (3)**
- **Made the text in the Quiet Mode list bigger:** the date labels and sub-info (day/week/month · date) lines were too small to read (0.5rem); bumped to readable sizes.
- **National (official) holidays no longer get an "eve" day — the day before now runs as a normal school day with the bell ringing:** removed "Republic Day Eve" from the auto-add list entirely. The eve/half-day concept in Turkey applies only to the two religious holidays (Ramadan/Eid al-Adha); national holidays don't have an equivalent eve.
- **The eve of Ramadan/Eid al-Adha is now a genuine "half day":** previously the eve day was silenced entirely, including the morning. Now the morning runs normally with bells ringing as usual, and only the afternoon (from 12:00 on) is automatically silenced. This required a new quiet-mode entry type ("Half Day — Afternoon") that only activates after noon. **Note:** if you already clicked "🎉 Add Official Holidays" before this update, the old (full-day-silent) eve entries won't update automatically — clear the Quiet Mode list ("🗑 Delete All") and click the button again to regenerate the correct (half-day) entries.

**September 1, 2026 (2)**
- **Fixed the actual root cause of some icons blinking continuously:** the previous fix (see the "September 1, 2026" entry below) only closed the DOM-write-timing gap; the underlying cause was three missing/mismatched SVG files. (1) The **📤 (export) and 📥 (restore)** icon files didn't exist at all in `svg/` — the "Export All Settings" and "Restore from Backup" buttons on the Shutdown/Channel panel were affected. (2) The **🩺 (System Health Check)** icon file was also missing — this is why the Manifest panel's header icon kept blinking non-stop. (3) For **⚠️ and ℹ️**, the twemoji library generates a codepoint with a "-fe0f" suffix, but the files on disk are named without it — these two icons (used in many places throughout the app) had the same problem. In all three cases: missing/mismatched file → browser 404 → icon reverts to the raw emoji character → the background observer notices and tries to convert it to SVG again → same 404 → reverts to raw character again... this loop repeated forever, producing the continuous "blinking". The three missing SVG files were added from twemoji's source repository, the "-fe0f" suffix mismatch was fixed in code, and as a safety net, an icon that fails to load once is now never retried again — preventing this same infinite loop from recurring if a file ever goes missing in the future.
- **The date in the header and About panel now actually stays fixed:** the version-date text in these two spots (`topbarDate`, `infoDate`) was being overwritten every second by the clock/date update function with the computer's **real/simulated current date** — so even after manually typing "September 2026", the screen always showed whatever month the system was actually on, making it look like "the date never changed". These two fields are now independent of the live clock; update the fixed text in the HTML directly to change the version date.

**September 1, 2026**
- **Fixed icon flicker on the Manifest and Prayer Times panels:** both panels built their content by writing raw emoji characters straight into the page, while the conversion to SVG icons happened in the background via a 200ms-debounced observer. As a result, every time either panel refreshed (opening the tab, pressing "🔄 Refresh", or the automatic 30-minute prayer-time update) the raw emoji would flash on screen for a moment before turning into the SVG icon, creating a "blinking" effect. This was already fixed elsewhere for frequently-updated content (the VU meter, the status line, etc.); that same fix has now been applied to the Manifest and Prayer Times panels — icons now appear as SVG immediately, with no flash.

**August 15, 2026 (3)**
- **Bell Planning page: Plan A / B / C are now tabbed:** previously all three plans were stacked on one long page (Plan A, then Plan B's settings + calendar, then Plan C's settings + calendar), and it wasn't obvious to a new visitor that three separate plans even existed. There are now **Ⓐ Plan A / Ⓑ Plan B / Ⓒ Plan C** tabs at the top of the panel — clicking one shows only that plan's settings (and calendar, where applicable). Whichever plan is currently active is automatically selected whenever the panel is opened. The actual plan-selection/apply logic (the radio button on each card, the "Apply & Save" buttons) is unchanged — only the layout was made clearer.

**August 15, 2026 (2)**
- **Prayer tolerance: separate "Before / After" minutes instead of one "± min":** the single tolerance field on the Prayer Times tab was replaced with separate fields for the time **before** and **after** a prayer. The old default (5 min) was widely felt to be too long — both now default to **2 minutes**.
- **Manual time edits now persist:** editing a single prayer time on the Prayer Times tab no longer gets silently reverted by the next automatic fetch. The edit stays fixed for that day (marked with a ✎ icon); only the times you didn't touch keep auto-updating. Use **↺ Reset Today** to go back to fully automatic times if needed.
- **Prayer-conflict warning in the bell table is now per-bell:** previously, if a row had more than one bell (e.g. Break Exit + Student Bell), only the first conflicting one was flagged and others were skipped. Each bell is now checked independently with its own time, so if multiple bells in the same row conflict, each gets its own red warning (including the student bell).

**August 15, 2026**
- **Fixed a language-selection bug (Raspberry Pi / English operating systems):** the program now **always starts in Turkish** on first launch. Previously, if the user had never picked a language, the program looked at the computer's/browser's operating-system language (`navigator.language`); on devices with an English OS (e.g. some Raspberry Pi setups) this made the program open directly in English without ever showing Turkish. That fallback has been removed entirely. A language the user **manually selected** is still remembered exactly as before — it's kept even after the program or computer restarts; only the incorrect OS-language fallback used when no choice had ever been made was fixed.
- **Added a prayer-conflict warning to the bell table:** on the main schedule table, when Prayer mode is active and a row's bell time conflicts with a prayer time (± tolerance), that row's **Notes** column now shows a red warning (e.g. *"Öğle Ezanı Saati. Ses Kapalı"* / "Noon Prayer Time. Sound Off"). Previously this conflict was only visible at the moment the bell was due to ring (via a toast notification); now it can be spotted ahead of time directly in the table. Only bells that are actually enabled (and would otherwise ring) are checked — disabled bells don't trigger a warning.

**August 1, 2026**
- **Fixed a permanent settings-loss issue:** the kiosk Chrome profile is now kept inside the program folder (`chrome-profil/`) instead of `%TEMP%` — some computers periodically clear the TEMP folder, which used to wipe localStorage (and therefore all settings).
- **Added a server-side settings backup:** the 4 most critical settings (the weekly bell schedule + weekend bell checkboxes, the "Show/Hide Table" preference, school info, and the active A/B/C plan) are now also written to `zil-ayarlar.json` via `zunucu/app_settings.py`. On every startup, the program reads this file first and writes it back into localStorage — so settings survive even if the browser profile is wiped entirely. New endpoints: `GET/POST /api/app-settings`.
- Confirmed that weekend bell checkboxes (Saturday/Sunday) are disabled by default.
- Removed the static "Last updated" line on the Manifest page (it needed manual updates and kept going stale). Fixed a few missing/incorrect lines: `zil-start.bat` → `zil-baslat.bat`, added the new `/api/app-settings` endpoints and the `zilAccordionView` localStorage key.
- Removed the unused, outdated root-level `en.json`/`tr.json` files — the app only ever used `locales/en.json` and `locales/tr.json`; the old files were a confusing duplicate missing 385 keys.

**July 1, 2026**
- **Plan C — Block Lessons** completely redesigned. The old "cut point" logic is replaced by a **group-based structure**: each group is defined as a Block Lesson or a Single Lesson, with how many lessons to merge, their duration, and the following gap (break/lunch) each configurable separately. Lessons within a block group are merged with no bell between them.
- **↺ Reset button:** the `↺ Default` button in the tab bar and the `↺ Reset` button in the toolbar were merged into a **single Reset button**. Pressing Reset now returns every day of the week to Plan A (previously `_gunPlanlar` wasn't reset, so days on Plan B/C didn't revert to A — fixed).
- **USB Arduino connection hardened:** added `arduino-usb-fix.bat` (disables USB Selective Suspend). Added `port.forget()` support in the Web Serial API — when the Arduino is unplugged and replugged, the browser cache is cleared and it reconnects. The port is now closed properly on `beforeunload`. USB `connect`/`disconnect` events are now listened for.
- The **Sound tab** was renamed to "Bell Sound Files".
- **About panel:** added a WhatsApp icon next to the phone number; clicking the icon opens WhatsApp Web (the number itself is no longer clickable, only the icon).
- Removed the version history from the Manifest page.

**June 20, 2026**
- Sound/announcement files selected from the Sound tab are now saved **automatically and permanently** — no need to press "Save" or reselect them; the setting survives a full restart.
- **Default bell sound (fallback):** if no custom file is uploaded for Break, Student, Teacher, or Assembly bells, they now automatically play the general `zil.mp3` — previously these bells stayed completely silent without a dedicated file; this is now fixed. In the settings panel, bell types running on the default sound show in orange, ones with a custom file show in green.
- The VU meter animation was rewritten so it no longer jitters the volume sliders next to it.
- The phone number in the About panel now opens a WhatsApp chat directly when clicked.

**June 16, 2026**
- Bell sounds were split apart: Break, Student, Teacher, and Assembly bells can now each use their own sound file (`zil_tenefus.mp3`, `zil_ogrenci.mp3`, `zil_ogretmen.mp3`, `zil_toplanma.mp3`). The old single `zil.mp3` is now used only for the manual button/RF remote.
- Added a new announcement for the break-exit bell (`anons_tenefus.mp3`).

---

## 👨‍💻 Developer Info

- **Design:** Mustafa Necati BOZOK
- **Coding:** Claude (Anthropic)
- **License:** Free for educational use
- **Last Updated:** September 1, 2026

---

*This README is written so that someone who has never seen the system before can follow every step and complete the installation.*
