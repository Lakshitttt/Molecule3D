"""
Molecule3D — Combined Flask Backend
=====================================
Combines:
  • v2  : VSEPR Bond Angle & Geometry Predictor  (/predict)
  • v3  : XYZ File Molecular Analyzer             (/analyze-xyz)

Run:
    pip install flask numpy
    python app.py
Then open http://127.0.0.1:5000
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# § 1 — VSEPR DATA  (unchanged from v2)
# ══════════════════════════════════════════════════════════════════════════════

MOLECULE_DB: dict[str, dict[str, int]] = {
    # ── Linear (bp=2, lp=0) ──────────────────────────────────────────────────
    "CO2":      {"bond_pairs": 2, "lone_pairs": 0},
    "BECL2":    {"bond_pairs": 2, "lone_pairs": 0},
    "HCN":      {"bond_pairs": 2, "lone_pairs": 0},
    "CS2":      {"bond_pairs": 2, "lone_pairs": 0},
    "NO2+":     {"bond_pairs": 2, "lone_pairs": 0},
    # ── Trigonal Planar (bp=3, lp=0) ─────────────────────────────────────────
    "BF3":      {"bond_pairs": 3, "lone_pairs": 0},
    "BCL3":     {"bond_pairs": 3, "lone_pairs": 0},
    "SO3":      {"bond_pairs": 3, "lone_pairs": 0},
    "NO3-":     {"bond_pairs": 3, "lone_pairs": 0},
    "CO3^2-":   {"bond_pairs": 3, "lone_pairs": 0},
    # ── Tetrahedral (bp=4, lp=0) ─────────────────────────────────────────────
    "CH4":      {"bond_pairs": 4, "lone_pairs": 0},
    "CCL4":     {"bond_pairs": 4, "lone_pairs": 0},
    "SICL4":    {"bond_pairs": 4, "lone_pairs": 0},
    "NH4+":     {"bond_pairs": 4, "lone_pairs": 0},
    "SO4^2-":   {"bond_pairs": 4, "lone_pairs": 0},
    "PO4^3-":   {"bond_pairs": 4, "lone_pairs": 0},
    # ── Trigonal Pyramidal (bp=3, lp=1) ──────────────────────────────────────
    "NH3":      {"bond_pairs": 3, "lone_pairs": 1},
    "PCL3":     {"bond_pairs": 3, "lone_pairs": 1},
    "ASH3":     {"bond_pairs": 3, "lone_pairs": 1},
    "PH3":      {"bond_pairs": 3, "lone_pairs": 1},
    "NCL3":     {"bond_pairs": 3, "lone_pairs": 1},
    # ── Bent (bp=2, lp=2) ────────────────────────────────────────────────────
    "H2O":      {"bond_pairs": 2, "lone_pairs": 2},
    "H2S":      {"bond_pairs": 2, "lone_pairs": 2},
    # ── Bent (bp=2, lp=1) — O3/SO2 type ─────────────────────────────────────
    "O3":       {"bond_pairs": 2, "lone_pairs": 1},
    "SO2":      {"bond_pairs": 2, "lone_pairs": 1},
    "SEO2":     {"bond_pairs": 2, "lone_pairs": 1},
    # ── Trigonal Bipyramidal (bp=5, lp=0) ────────────────────────────────────
    "PCL5":     {"bond_pairs": 5, "lone_pairs": 0},
    "PF5":      {"bond_pairs": 5, "lone_pairs": 0},
    "ASF5":     {"bond_pairs": 5, "lone_pairs": 0},
    # ── Seesaw (bp=4, lp=1) ──────────────────────────────────────────────────
    "SF4":      {"bond_pairs": 4, "lone_pairs": 1},
    "SEF4":     {"bond_pairs": 4, "lone_pairs": 1},
    "TEF4":     {"bond_pairs": 4, "lone_pairs": 1},
    # ── T-shaped (bp=3, lp=2) ────────────────────────────────────────────────
    "CLF3":     {"bond_pairs": 3, "lone_pairs": 2},
    "BRF3":     {"bond_pairs": 3, "lone_pairs": 2},
    "ICL3":     {"bond_pairs": 3, "lone_pairs": 2},
    # ── Linear via sp3d (bp=2, lp=3) ─────────────────────────────────────────
    "XEF2":     {"bond_pairs": 2, "lone_pairs": 3},
    "I3-":      {"bond_pairs": 2, "lone_pairs": 3},
    "BRF2-":    {"bond_pairs": 2, "lone_pairs": 3},
    # ── Octahedral (bp=6, lp=0) ──────────────────────────────────────────────
    "SF6":      {"bond_pairs": 6, "lone_pairs": 0},
    "SEF6":     {"bond_pairs": 6, "lone_pairs": 0},
    "PF6-":     {"bond_pairs": 6, "lone_pairs": 0},
    # ── Square Pyramidal (bp=5, lp=1) ────────────────────────────────────────
    "BRF5":     {"bond_pairs": 5, "lone_pairs": 1},
    "IF5":      {"bond_pairs": 5, "lone_pairs": 1},
    "XEOF4":    {"bond_pairs": 5, "lone_pairs": 1},
    # ── Square Planar (bp=4, lp=2) ───────────────────────────────────────────
    "XEF4":     {"bond_pairs": 4, "lone_pairs": 2},
    "ICL4-":    {"bond_pairs": 4, "lone_pairs": 2},
    "BRF4-":    {"bond_pairs": 4, "lone_pairs": 2},
    "PTCL4^2-": {"bond_pairs": 4, "lone_pairs": 2},
    # ── Additional ───────────────────────────────────────────────────────────
    "N2O":      {"bond_pairs": 2, "lone_pairs": 0},
    "CH2O":     {"bond_pairs": 3, "lone_pairs": 0},
    "CF4":      {"bond_pairs": 4, "lone_pairs": 0},
    "CH3F":     {"bond_pairs": 4, "lone_pairs": 0},
    "CH2CL2":   {"bond_pairs": 4, "lone_pairs": 0},
    "PO43-":    {"bond_pairs": 4, "lone_pairs": 0},
    "SO3^2-":   {"bond_pairs": 3, "lone_pairs": 1},
    "H3O+":     {"bond_pairs": 3, "lone_pairs": 1},
    "OF2":      {"bond_pairs": 2, "lone_pairs": 2},
    "NO2-":     {"bond_pairs": 2, "lone_pairs": 1},
    "WF6":      {"bond_pairs": 6, "lone_pairs": 0},
}

VSEPR_TABLE: dict[tuple[int, int], tuple[str, str, str]] = {
    (2, 0): ("Linear",               "180°",        "sp"),
    (3, 0): ("Trigonal Planar",      "120°",        "sp²"),
    (4, 0): ("Tetrahedral",          "109.5°",      "sp³"),
    (4, 1): ("Trigonal Pyramidal",   "~107°",       "sp³"),
    (4, 2): ("Bent",                 "~104.5°",     "sp³"),
    (3, 1): ("Bent",                 "~120°",       "sp²"),
    (5, 0): ("Trigonal Bipyramidal", "90°, 120°",   "sp³d"),
    (5, 1): ("Seesaw",               "<90°, <120°", "sp³d"),
    (5, 2): ("T-shaped",             "~90°",        "sp³d"),
    (5, 3): ("Linear",               "180°",        "sp³d"),
    (6, 0): ("Octahedral",           "90°",         "sp³d²"),
    (6, 1): ("Square Pyramidal",     "~90°",        "sp³d²"),
    (6, 2): ("Square Planar",        "90°",         "sp³d²"),
}


# ══════════════════════════════════════════════════════════════════════════════
# § 2 — XYZ ANALYZER CORE  (ported & cleaned from v3)
# ══════════════════════════════════════════════════════════════════════════════

# Covalent radii in Ångströms (Alvarez 2008)
ATOMIC_RADII: dict[str, float] = {
    "H":  0.31, "HE": 0.28,
    "LI": 1.28, "BE": 0.96, "B":  0.84, "C":  0.76, "N":  0.71,
    "O":  0.66, "F":  0.57, "NE": 0.58,
    "NA": 1.66, "MG": 1.41, "AL": 1.21, "SI": 1.11, "P":  1.07,
    "S":  1.05, "CL": 1.02, "AR": 1.06,
    "K":  2.03, "CA": 1.76, "FE": 1.32, "CU": 1.32, "ZN": 1.22,
    "BR": 1.20, "I":  1.39,
}

BOND_TOLERANCE = 1.2   # multiplier on sum of covalent radii
DEFAULT_RADIUS = 0.77  # fallback for unknown elements


class Atom:
    """Minimal atom container parsed from an XYZ file."""
    __slots__ = ("index", "symbol", "coords")

    def __init__(self, index: int, symbol: str, coords: np.ndarray) -> None:
        self.index  = index
        self.symbol = symbol
        self.coords = coords   # np.ndarray shape (3,)


def _normalise_symbol(raw: str) -> str:
    """'cl' → 'Cl',  'C' → 'C'."""
    s = raw.strip()
    return (s[0].upper() + s[1:].lower()) if len(s) > 1 else s.upper()


def _parse_xyz(text: str) -> list[Atom]:
    """
    Parse XYZ text into Atom objects.
    Raises ValueError with a user-readable message on bad input.
    """
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]

    if len(lines) < 3:
        raise ValueError("File too short — need at least: atom count, comment, one atom.")

    try:
        n_atoms = int(lines[0].strip())
    except ValueError:
        raise ValueError(f"First line must be an integer (atom count); got: '{lines[0]}'")

    atom_lines = lines[2:]   # skip comment line
    if len(atom_lines) < n_atoms:
        raise ValueError(
            f"Header says {n_atoms} atoms but only {len(atom_lines)} records found."
        )

    atoms: list[Atom] = []
    for i, line in enumerate(atom_lines[:n_atoms]):
        parts = line.split()
        if len(parts) < 4:
            raise ValueError(f"Atom record {i + 1} malformed (need: symbol x y z): '{line}'")
        try:
            coords = np.array([float(parts[1]), float(parts[2]), float(parts[3])],
                              dtype=np.float64)
        except ValueError:
            raise ValueError(f"Non-numeric coordinate on atom record {i + 1}: '{line}'")
        atoms.append(Atom(i, _normalise_symbol(parts[0]), coords))

    return atoms


def _atom_radius(symbol: str) -> float:
    return ATOMIC_RADII.get(symbol.upper(), DEFAULT_RADIUS)


def _detect_bonds(atoms: list[Atom]) -> list[tuple[int, int, float]]:
    """
    Return (i, j, distance_Å) for every bonded pair using the
    covalent-radii criterion: dist < (r_i + r_j) × BOND_TOLERANCE.
    Sorted by ascending distance.
    """
    bonds: list[tuple[int, int, float]] = []
    for (i, a), (j, b) in combinations(enumerate(atoms), 2):
        dist = float(np.linalg.norm(a.coords - b.coords))
        if dist < (_atom_radius(a.symbol) + _atom_radius(b.symbol)) * BOND_TOLERANCE:
            bonds.append((i, j, round(dist, 4)))
    bonds.sort(key=lambda t: t[2])
    return bonds


def _build_adjacency(n: int, bonds: list[tuple[int, int, float]]) -> dict[int, list[int]]:
    adj: dict[int, list[int]] = defaultdict(list)
    for i, j, _ in bonds:
        adj[i].append(j)
        adj[j].append(i)
    return dict(adj)


def _angle_deg(v1: np.ndarray, v2: np.ndarray) -> float:
    cos = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return float(np.degrees(np.arccos(np.clip(cos, -1.0, 1.0))))


def _dihedral_deg(p0: np.ndarray, p1: np.ndarray,
                  p2: np.ndarray, p3: np.ndarray) -> float:
    """Praxeolitic atan2 dihedral — numerically stable."""
    b1 = p1 - p0
    b2 = p2 - p1
    b3 = p3 - p2
    n1 = np.cross(b1, b2)
    n2 = np.cross(b2, b3)
    norm_b2 = np.linalg.norm(b2)
    if norm_b2 < 1e-10:
        return 0.0
    b2h = b2 / norm_b2
    m1  = np.cross(n1, b2h)
    return float(np.degrees(np.arctan2(np.dot(m1, n2), np.dot(n1, n2))))


def _compute_bond_angles(
    atoms: list[Atom],
    bonds: list[tuple[int, int, float]],
    adj:   dict[int, list[int]],
) -> list[dict]:
    """Bond angles for all bonded triplets A–B–C (no duplicates)."""
    seen: set[tuple[int, int, int]] = set()
    results: list[dict] = []

    for b_idx, neighbours in adj.items():
        if len(neighbours) < 2:
            continue
        b = atoms[b_idx]
        for a_idx, c_idx in combinations(neighbours, 2):
            key = (min(a_idx, c_idx), b_idx, max(a_idx, c_idx))
            if key in seen:
                continue
            seen.add(key)
            v_ba = atoms[a_idx].coords - b.coords
            v_bc = atoms[c_idx].coords - b.coords
            angle = round(_angle_deg(v_ba, v_bc), 2)
            results.append({
                "label": f"{atoms[a_idx].symbol}–{b.symbol}–{atoms[c_idx].symbol}",
                "value": angle,
            })

    results.sort(key=lambda d: d["label"])
    return results


def _compute_dihedral_angles(
    atoms: list[Atom],
    bonds: list[tuple[int, int, float]],
    adj:   dict[int, list[int]],
) -> list[dict]:
    """Dihedral angles for all bonded chains A–B–C–D (no duplicates)."""
    seen: set[tuple[int, int, int, int]] = set()
    results: list[dict] = []

    for b_idx, c_idx, _ in bonds:
        for a_idx in adj.get(b_idx, []):
            if a_idx == c_idx:
                continue
            for d_idx in adj.get(c_idx, []):
                if d_idx in (b_idx, a_idx):
                    continue
                fwd = (a_idx, b_idx, c_idx, d_idx)
                rev = (d_idx, c_idx, b_idx, a_idx)
                key = min(fwd, rev)
                if key in seen:
                    continue
                seen.add(key)
                dih = round(_dihedral_deg(
                    atoms[a_idx].coords, atoms[b_idx].coords,
                    atoms[c_idx].coords, atoms[d_idx].coords,
                ), 2)
                results.append({
                    "label": (
                        f"{atoms[a_idx].symbol}–{atoms[b_idx].symbol}"
                        f"–{atoms[c_idx].symbol}–{atoms[d_idx].symbol}"
                    ),
                    "value": dih,
                })

    results.sort(key=lambda d: d["label"])
    return results


def _molecular_formula(atoms: list[Atom]) -> str:
    """Hill order: C → H → alphabetical."""
    counts = Counter(a.symbol for a in atoms)
    order = [s for s in ("C", "H") if s in counts]
    order += sorted(s for s in counts if s not in ("C", "H"))
    return "".join(s if counts[s] == 1 else f"{s}{counts[s]}" for s in order)


# ══════════════════════════════════════════════════════════════════════════════
# § 3 — FLASK ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Serve the single-page frontend."""
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """
    VSEPR geometry prediction (v2 feature — unchanged).
    POST JSON:
      { "mode": "molecule", "molecule": "CH4" }
      { "mode": "manual",   "bond_pairs": 4, "lone_pairs": 0 }
    """
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid or missing JSON."}), 400

    mode = data.get("mode")

    if mode == "molecule":
        name = data.get("molecule", "").strip().upper()
        if name not in MOLECULE_DB:
            return jsonify({
                "error": "Molecule not found. Please enter bond pairs and lone pairs."
            }), 404
        bp = MOLECULE_DB[name]["bond_pairs"]
        lp = MOLECULE_DB[name]["lone_pairs"]

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

    result = VSEPR_TABLE.get((bp + lp, lp))
    if result is None:
        return jsonify({"error": "This configuration is not supported."}), 200

    geometry, angle, hybrid = result
    return jsonify({
        "geometry":      geometry,
        "angle":         angle,
        "hybridization": hybrid,
        "bond_pairs":    bp,
        "lone_pairs":    lp,
    })


@app.route("/analyze-xyz", methods=["POST"])
def analyze_xyz():
    """
    XYZ file molecular analysis (v3 feature).
    Accepts a multipart file upload with field name 'xyz_file'.
    Returns JSON with formula, stats, bonds, angles, and dihedral angles.
    """
    if "xyz_file" not in request.files:
        return jsonify({"error": "No file uploaded. Send field 'xyz_file'."}), 400

    f = request.files["xyz_file"]
    if f.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    try:
        text = f.read().decode("utf-8", errors="replace")
    except Exception:
        return jsonify({"error": "Could not read the uploaded file."}), 400

    # Parse atoms
    try:
        atoms = _parse_xyz(text)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 422

    if not atoms:
        return jsonify({"error": "No atoms found in the file."}), 422

    # Detect bonds & build adjacency
    bonds = _detect_bonds(atoms)
    adj   = _build_adjacency(len(atoms), bonds)

    # Bond length stats
    lengths = [d for _, _, d in bonds]
    avg_len = round(float(np.mean(lengths)), 2) if lengths else 0.0
    min_len = round(min(lengths), 2)            if lengths else 0.0
    max_len = round(max(lengths), 2)            if lengths else 0.0

    # Serialise bond list
    bond_list = [
        {
            "label": f"{atoms[i].symbol}–{atoms[j].symbol}",
            "value": round(dist, 2),
        }
        for i, j, dist in bonds
    ]

    return jsonify({
        "formula":         _molecular_formula(atoms),
        "total_atoms":     len(atoms),
        "total_bonds":     len(bonds),
        "avg_bond_length": avg_len,
        "min_bond_length": min_len,
        "max_bond_length": max_len,
        "bonds":           bond_list,
        "angles":          _compute_bond_angles(atoms, bonds, adj),
        "dihedrals":       _compute_dihedral_angles(atoms, bonds, adj),
    })


# ══════════════════════════════════════════════════════════════════════════════
# § 4 — ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import os
    app.run(debug=os.environ.get("FLASK_DEBUG", "False").lower() == "true")
