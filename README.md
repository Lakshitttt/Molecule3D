# Bond Angle & Geometry Predictor

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
python app.py

# 3. Open in browser
http://127.0.0.1:5000
```

## File Structure

```
bond-geometry-predictor/
├── app.py               ← Flask backend
├── templates/
│   └── index.html       ← Single-page UI
├── static/
│   ├── style.css        ← All styles
│   └── script.js        ← Mode switching & API calls
├── Procfile             ← Heroku / Gunicorn deployment config
├── requirements.txt     ← Python dependencies
└── README.md
```

## Supported Molecules (auto-lookup)
The database has been expanded to support **over 50 molecules/ions**. A small sample includes:

| Molecule | Bond Pairs | Lone Pairs | Geometry            |
|----------|-----------|------------|---------------------|
| CH4      | 4         | 0          | Tetrahedral 109.5°  |
| NH3      | 3         | 1          | Trigonal Pyramidal ~107° |
| H2O      | 2         | 2          | Bent ~104.5°        |
| CO2      | 2         | 0          | Linear 180°         |
| BF3      | 3         | 0          | Trigonal Planar 120°|
| SF6      | 6         | 0          | Octahedral 90°      |

## VSEPR Configurations Supported
| Bond Pairs | Lone Pairs | Geometry            | Angle         | Hybrid |
|-----------|------------|---------------------|---------------|--------|
| 2         | 0          | Linear              | 180°          | sp     |
| 3         | 0          | Trigonal Planar     | 120°          | sp²    |
| 3         | 1          | Bent                | ~120°         | sp²    |
| 4         | 0          | Tetrahedral         | 109.5°        | sp³    |
| 4         | 1          | Trigonal Pyramidal  | ~107°         | sp³    |
| 2         | 2          | Bent                | ~104.5°       | sp³    |
| 5         | 0          | Trigonal Bipyramidal| 90°, 120°     | sp³d   |
| 4         | 1          | Seesaw              | <90°, <120°   | sp³d   |
| 3         | 2          | T-shaped            | ~90°          | sp³d   |
| 2         | 3          | Linear              | 180°          | sp³d   |
| 6         | 0          | Octahedral          | 90°           | sp³d²  |
| 5         | 1          | Square Pyramidal    | ~90°          | sp³d²  |
| 4         | 2          | Square Planar       | 90°           | sp³d²  |
