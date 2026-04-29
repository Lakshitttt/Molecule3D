# Molecule3D — Desktop App

A native desktop application wrapping the Molecule3D Flask backend
using **pywebview**. The full web UI (VSEPR Predictor + XYZ Analyzer
+ 3D Viewer) runs inside a native OS window — no browser required.

## Install & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the desktop app
python main.py
```

That's it. A native window opens automatically.

## How it works

```
main.py
  │
  ├── Starts Flask (app.py) on a random free port in a daemon thread
  ├── Waits until Flask is ready to accept connections
  └── Opens a pywebview window pointed at http://127.0.0.1:<port>
        │
        ├── GET  /          → templates/index.html  (Jinja2)
        ├── POST /predict   → VSEPR geometry prediction
        └── POST /analyze-xyz → XYZ molecular analysis
```

Flask serves the same `templates/index.html`, `static/style.css`, and
`static/script.js` that the web version uses — nothing was changed.

## File structure

```
molecule3d-desktop/
├── main.py              ← Desktop entry point (pywebview)
├── app.py               ← Flask backend (unchanged)
├── requirements.txt
├── templates/
│   └── index.html       ← Single-page UI (unchanged)
└── static/
    ├── style.css        ← All styles (unchanged)
    └── script.js        ← Mode switching & API calls (unchanged)
```

## Platform notes

| Platform | Backend used by pywebview       |
|----------|---------------------------------|
| Windows  | WebView2 (Edge Chromium)        |
| macOS    | WKWebView                       |
| Linux    | GTK WebKit2 (`python3-gi` pkg)  |

On Linux you may need to install the GTK WebKit2 system package:

```bash
# Debian/Ubuntu
sudo apt install python3-gi python3-gi-cairo gir1.2-webkit2-4.0

# Fedora/RHEL
sudo dnf install python3-gobject webkit2gtk4.0
```
