# SWL Bitácora · EA5XQ

> Browser-based SWL monitoring and logbook for **Yaesu FT-920** and **Icom IC-756**,
> connecting directly to the radio via the **Web Serial API** — no drivers, no software to install.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-brightgreen?style=for-the-badge)](https://ea5xq.github.io/swl_bitacora/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)
[![Web Serial API](https://img.shields.io/badge/Requires-Chrome%20%2F%20Edge-orange?style=for-the-badge)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Serial_API)

---

## ✨ Features

| Panel | What it does |
|---|---|
| **My Favourites** | 251 stations imported from SDR# memory (Frequencies.xml), grouped and searchable. Click any row to tune the radio via CAT |
| **EiBi world database** | 9,396 shortwave stations (season A26), searchable by name, country or frequency. Shows live ON-AIR / OFF-AIR / IRREGULAR status based on UTC schedule |
| **Logbook** | 341 historical receptions imported from DX Toolbox, plus new entries you add from the UI. Searchable, editable, deletable. One-click re-tune from any log entry |
| **NDB map** | 31 NDBs heard, plotted on a Leaflet/CartoDB map via OurAirports data |
| **Reminders** | Set an alert on any EiBi station — a toast notification (and browser notification if permitted) fires when the transmission window opens, with a one-click tune button |
| **Frequency monitor** | Reads frequency and mode from the radio every 2 s (read-only). Identifies the station from EiBi in real time. Auto-recovers on consecutive read failures |

---

## 🚀 Live Demo

**[https://ea5xq.github.io/swl_bitacora/](https://ea5xq.github.io/swl_bitacora/)**

> **Requirements:**
> - Google Chrome or Microsoft Edge — Firefox does not support Web Serial API
> - FT-920 or IC-756 connected via a USB–serial adapter
> - HTTPS (GitHub Pages satisfies this automatically)

---

## 🔌 Connecting

| Radio | Baud rate | Settings | Notes |
|---|---|---|---|
| Yaesu FT-920 | 4800 | 8N2 | CAT binary protocol |
| Icom IC-756 | 9600 | 8N1 | CI-V address 0x58 |

1. Open the [Live Demo](https://ea5xq.github.io/swl_bitacora/) in Chrome or Edge.
2. Select your radio from the dropdown.
3. Click **Conectar** — the browser serial port picker appears.
4. Select the correct COM / tty port and connect.
5. Click **Activar monitor** to start reading frequency and mode.

---

## 🛠 Running Locally

Single HTML file — no build step for the app itself:

```bash
git clone https://github.com/ea5xq/swl_bitacora.git
cd swl_bitacora
# Open index.html in Chrome or Edge
```

---

## 🔄 Updating the Station Database

### Update favourites (from SDR# memory export)

1. In SDR#: Manage Memories → Export → save as `Frequencies.xml`
2. Replace `Frequencies.xml` in the repo with the new export
3. Run the build script:

```bash
python3 build_ft920_control.py Frequencies.xml index.html
```

This **only** updates `const STATIONS` and `const GROUP_LABELS` in `index.html`.
The EiBi database, logbook and all other code are untouched.

### Update EiBi (from eibispace.de)

1. Download the current schedule CSV from [eibispace.de](https://www.eibispace.de) (e.g. `sked-a26.csv`)
2. Run:

```bash
python3 build_eibi.py sked-a26.csv index.html
```

This **only** updates `const EIBI` in `index.html`. Your favourites and all other code are untouched.

Both scripts are independent and can be run in any order.

> **Note:** EiBi CSV files are excluded from the repo via `.gitignore` (they are large — ~3 MB — and downloadable fresh from eibispace.de at any time).

---

## 📡 Protocols

### Yaesu FT-920 — binary CAT

- 5-byte commands: `[P4, P3, P2, P1, OPCODE]`
- Frequency encoded as 4-byte BCD, MSB first
- `READ_OP_DATA` command (opcode `0x10`) returns 28 bytes including frequency, mode and VFO state
- Mode set via opcode `0x0C`; VFO-A frequency set via opcode `0x0A`

### Icom IC-756 — CI-V

- Frame structure: `FE FE <dest> <ctrl> <cmd> [data] FD`
- CI-V address: **0x58** (confirm in your radio's menu if different)
- Controller address: `0xE0` (standard PC address in Icom ecosystem)
- Frequency: 5-byte packed BCD, LSB first
- Commands: `0x03` read freq, `0x04` read mode, `0x05` set freq, `0x06` set mode

---

## 📂 Repository Structure

```
swl_bitacora/
├── index.html                 ← the application (generated — do not edit manually)
├── build_ft920_control.py     ← updates STATIONS from Frequencies.xml
├── build_eibi.py              ← updates EIBI from eibispace.de CSV
├── Frequencies.xml            ← SDR# memory export (source of truth for favourites)
├── README.md
├── LICENSE
├── .gitignore
└── .nojekyll                  ← disables Jekyll on GitHub Pages
```

`index.html` is the **output** of the two build scripts. It is checked into the repo so GitHub Pages serves it directly without a build step.

---

## ⚠️ Disclaimer

This software is provided for personal, experimental use and is offered **"as is" without warranty of any kind**.

It has been tested on the author's own equipment (EA5XQ — Yaesu FT-920 and Icom IC-756) and works correctly in that setup. The author accepts no responsibility for any damage to radio equipment, loss of data, or unintended transmissions that may result from its use.

Specific points to be aware of:

- **Tuning commands** — clicking a station row sends frequency and mode to the radio via CAT/CI-V. Verify your radio's baud rate and, for the IC-756, the CI-V address (default assumed: 0x58) before connecting.
- **Monitor mode** — the frequency/mode monitor is strictly read-only; it never writes to the radio while active.
- **Logbook** — new entries are stored in browser `localStorage` only. They are not synced anywhere and will be lost if you clear your browser data. Export regularly if the log matters to you.

Use at your own risk. The MIT licence in this repository includes a full limitation-of-liability clause.

---

## 🪪 Licence

MIT — see [LICENSE](LICENSE).  
© 2026 Juan · EA5XQ — [QRZ.com](https://www.qrz.com/db/EA5XQ)

Station database: [EiBi](https://www.eibispace.de) (public domain).  
NDB locations: [OurAirports](https://ourairports.com/data/) (public domain).  
Map tiles: © OpenStreetMap contributors, © CARTO.
