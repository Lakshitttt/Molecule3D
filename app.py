"""
Bond Angle & Geometry Predictor - Flask Backend
================================================
Run:  pip install flask
      python app.py
Then open http://127.0.0.1:5000
"""

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ── Molecule Database ────────────────────────────────────────────────────────
# Maps common molecule formulas → (bond_pairs, lone_pairs)
# Extend this dict to support more molecules.
MOLECULE_DB = {
    # ── Linear (bp=2, lp=0) ──────────────────────────────────────────────────
    "CO2":    {"bond_pairs": 2, "lone_pairs": 0},
    "BECL2":  {"bond_pairs": 2, "lone_pairs": 0},
    "HCN":    {"bond_pairs": 2, "lone_pairs": 0},
    "CS2":    {"bond_pairs": 2, "lone_pairs": 0},
    "NO2+":   {"bond_pairs": 2, "lone_pairs": 0},

    # ── Trigonal Planar (bp=3, lp=0) ─────────────────────────────────────────
    "BF3":    {"bond_pairs": 3, "lone_pairs": 0},
    "BCL3":   {"bond_pairs": 3, "lone_pairs": 0},
    "SO3":    {"bond_pairs": 3, "lone_pairs": 0},
    "NO3-":   {"bond_pairs": 3, "lone_pairs": 0},
    "CO3^2-": {"bond_pairs": 3, "lone_pairs": 0},

    # ── Tetrahedral (bp=4, lp=0) ──────────────────────────────────────────────
    "CH4":    {"bond_pairs": 4, "lone_pairs": 0},
    "CCL4":   {"bond_pairs": 4, "lone_pairs": 0},
    "SICL4":  {"bond_pairs": 4, "lone_pairs": 0},
    "NH4+":   {"bond_pairs": 4, "lone_pairs": 0},
    "SO4^2-": {"bond_pairs": 4, "lone_pairs": 0},
    "PO4^3-": {"bond_pairs": 4, "lone_pairs": 0},

    # ── Trigonal Pyramidal (bp=3, lp=1) ──────────────────────────────────────
    "NH3":    {"bond_pairs": 3, "lone_pairs": 1},
    "PCL3":   {"bond_pairs": 3, "lone_pairs": 1},
    "ASH3":   {"bond_pairs": 3, "lone_pairs": 1},
    "PH3":    {"bond_pairs": 3, "lone_pairs": 1},
    "NCL3":   {"bond_pairs": 3, "lone_pairs": 1},

    # ── Bent (bp=2, lp=2) ────────────────────────────────────────────────────
    "H2O":    {"bond_pairs": 2, "lone_pairs": 2},
    "H2S":    {"bond_pairs": 2, "lone_pairs": 2},

    # ── Bent (bp=2, lp=1) — O3/SO2 type ─────────────────────────────────────
    "O3":     {"bond_pairs": 2, "lone_pairs": 1},
    "SO2":    {"bond_pairs": 2, "lone_pairs": 1},
    "SEO2":   {"bond_pairs": 2, "lone_pairs": 1},

    # ── Trigonal Bipyramidal (bp=5, lp=0) ────────────────────────────────────
    "PCL5":   {"bond_pairs": 5, "lone_pairs": 0},
    "PF5":    {"bond_pairs": 5, "lone_pairs": 0},
    "ASF5":   {"bond_pairs": 5, "lone_pairs": 0},

    # ── Seesaw (bp=4, lp=1) ──────────────────────────────────────────────────
    "SF4":    {"bond_pairs": 4, "lone_pairs": 1},
    "SEF4":   {"bond_pairs": 4, "lone_pairs": 1},
    "TEF4":   {"bond_pairs": 4, "lone_pairs": 1},

    # ── T-shaped (bp=3, lp=2) ────────────────────────────────────────────────
    "CLF3":   {"bond_pairs": 3, "lone_pairs": 2},
    "BRF3":   {"bond_pairs": 3, "lone_pairs": 2},
    "ICL3":   {"bond_pairs": 3, "lone_pairs": 2},

    # ── Linear via sp3d (bp=2, lp=3) ─────────────────────────────────────────
    "XEF2":   {"bond_pairs": 2, "lone_pairs": 3},
    "I3-":    {"bond_pairs": 2, "lone_pairs": 3},
    "BRF2-":  {"bond_pairs": 2, "lone_pairs": 3},

    # ── Octahedral (bp=6, lp=0) ──────────────────────────────────────────────
    "SF6":    {"bond_pairs": 6, "lone_pairs": 0},
    "SEF6":   {"bond_pairs": 6, "lone_pairs": 0},
    "PF6-":   {"bond_pairs": 6, "lone_pairs": 0},

    # ── Square Pyramidal (bp=5, lp=1) ────────────────────────────────────────
    "BRF5":   {"bond_pairs": 5, "lone_pairs": 1},
    "IF5":    {"bond_pairs": 5, "lone_pairs": 1},
    "XEOF4":  {"bond_pairs": 5, "lone_pairs": 1},

    # ── Square Planar (bp=4, lp=2) ───────────────────────────────────────────
    "XEF4":   {"bond_pairs": 4, "lone_pairs": 2},
    "ICL4-":  {"bond_pairs": 4, "lone_pairs": 2},
    "BRF4-":  {"bond_pairs": 4, "lone_pairs": 2},
    "PTCL4^2-": {"bond_pairs": 4, "lone_pairs": 2},

    # ── Additional Polyatomic / Extended Matches ─────────────────────────────
    "N2O":    {"bond_pairs": 2, "lone_pairs": 0},
    "CH2O":   {"bond_pairs": 3, "lone_pairs": 0},
    "CF4":    {"bond_pairs": 4, "lone_pairs": 0},
    "CH3F":   {"bond_pairs": 4, "lone_pairs": 0},
    "CH2CL2": {"bond_pairs": 4, "lone_pairs": 0},
    "PO43-":  {"bond_pairs": 4, "lone_pairs": 0},
    "SO3^2-": {"bond_pairs": 3, "lone_pairs": 1},
    "H3O+":   {"bond_pairs": 3, "lone_pairs": 1},
    "OF2":    {"bond_pairs": 2, "lone_pairs": 2},
    "NO2-":   {"bond_pairs": 2, "lone_pairs": 1},
    "WF6":    {"bond_pairs": 6, "lone_pairs": 0},
}

# ── VSEPR Lookup Table ───────────────────────────────────────────────────────
# Key: (total_electron_pairs, lone_pairs)
# Value: (geometry_name, bond_angle, hybridization)
VSEPR_TABLE = {
    (2, 0): ("Linear",                "180°",        "sp"),
    (3, 0): ("Trigonal Planar",       "120°",        "sp²"),
    (4, 0): ("Tetrahedral",           "109.5°",      "sp³"),
    (4, 1): ("Trigonal Pyramidal",    "~107°",       "sp³"),
    (4, 2): ("Bent",                  "~104.5°",     "sp³"),
    (3, 1): ("Bent",                  "~120°",       "sp²"),  # O3/SO2 type

    # ── sp³d (5 electron pairs) ───────────────────────────────────────────────
    (5, 0): ("Trigonal Bipyramidal",  "90°, 120°",   "sp³d"),
    (5, 1): ("Seesaw",                "<90°, <120°", "sp³d"),
    (5, 2): ("T-shaped",              "~90°",        "sp³d"),
    (5, 3): ("Linear",                "180°",        "sp³d"),

    # ── sp³d² (6 electron pairs) ──────────────────────────────────────────────
    (6, 0): ("Octahedral",            "90°",         "sp³d²"),
    (6, 1): ("Square Pyramidal",      "~90°",        "sp³d²"),
    (6, 2): ("Square Planar",         "90°",         "sp³d²"),
}


@app.route("/")
def index():
    """Serve the single-page frontend."""
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """
    POST /predict
    Accepts JSON with two modes:
      molecule mode → { "mode": "molecule", "molecule": "CH4" }
      manual mode   → { "mode": "manual", "bond_pairs": 4, "lone_pairs": 0 }

    Returns geometry data or an error message.
    """
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid or missing JSON."}), 400
        
    mode = data.get("mode")

    # ── Mode: molecule lookup ────────────────────────────────────────────────
    if mode == "molecule":
        name = data.get("molecule", "").strip().upper()
        if name not in MOLECULE_DB:
            # Instruct the frontend to switch to manual input mode
            return jsonify({
                "error": "Molecule not found. Please enter bond pairs and lone pairs."
            }), 404

        bp = MOLECULE_DB[name]["bond_pairs"]
        lp = MOLECULE_DB[name]["lone_pairs"]

    # ── Mode: manual entry ───────────────────────────────────────────────────
    elif mode == "manual":
        try:
            bp = int(data.get("bond_pairs", -1))
            lp = int(data.get("lone_pairs", -1))
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid bond/lone pair values."}), 400

        if bp < 0 or lp < 0:
            return jsonify({"error": "Bond pairs and lone pairs must be non-negative."}), 400

    else:
        return jsonify({"error": "Unknown mode."}), 400

    # ── VSEPR geometry resolution ────────────────────────────────────────────
    total = bp + lp
    result = VSEPR_TABLE.get((total, lp))

    if result is None:
        return jsonify({"error": "This configuration is not supported."}), 200

    geometry, angle, hybrid = result
    return jsonify({
        "geometry":       geometry,
        "angle":          angle,
        "hybridization":  hybrid,
        "bond_pairs":     bp,
        "lone_pairs":     lp,
    })


if __name__ == "__main__":
    import os
    app.run(debug=os.environ.get("FLASK_DEBUG", "False").lower() == "true")
