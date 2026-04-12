/**
 * Bond Angle & Geometry Predictor — script.js
 * =============================================
 * Handles:
 *   1. Mode switching        (molecule ↔ manual)
 *   2. API call              (POST /predict)
 *   3. Error handling        (auto-switch on molecule-not-found)
 *   4. Result rendering      (data cards)
 *   5. 3D Viewer             (Three.js, pre-built scenes, drag+zoom)
 */

// ══════════════════════════════════════════════════════════════════════════════
// § 1 — PRE-DEFINED 3D GEOMETRY SCENES
// ══════════════════════════════════════════════════════════════════════════════
/*
  Each entry in GEOMETRY_SCENES is a static description of a molecular shape.
  Nothing is generated at runtime — the atoms and bonds are fixed coordinates
  that accurately represent each VSEPR geometry.

  Structure of each scene:
    atoms  : [{x, y, z, type}]  — type: 'central' | 'bonded' | 'lone'
    bonds  : [[indexA, indexB]] — pairs of atom indices to connect with a cylinder

  Colors (matched to legend in HTML):
    central → teal   #14b8a6
    bonded  → amber  #f59e0b
    lone    → grey   #94a3b8  (semi-transparent, shown as small fuzzy sphere)
*/
const GEOMETRY_SCENES = {

  // ── Linear (180°) ─────────────────────────────────────────────────────────
  // Two bonded atoms directly opposite the central atom. e.g. CO2
  "Linear": {
    atoms: [
      { x:  0,    y: 0, z: 0, type: 'central' },
      { x:  1.6,  y: 0, z: 0, type: 'bonded'  },
      { x: -1.6,  y: 0, z: 0, type: 'bonded'  },
    ],
    bonds: [[0,1],[0,2]],
  },

  // ── Trigonal Planar (120°) ────────────────────────────────────────────────
  // Three bonded atoms in a flat triangle. e.g. BF3
  "Trigonal Planar": {
    atoms: [
      { x:  0,     y: 0, z: 0,     type: 'central' },
      { x:  1.6,   y: 0, z: 0,     type: 'bonded'  },
      { x: -0.8,   y: 0, z:  1.386, type: 'bonded'  },
      { x: -0.8,   y: 0, z: -1.386, type: 'bonded'  },
    ],
    bonds: [[0,1],[0,2],[0,3]],
  },

  // ── Tetrahedral (109.5°) ──────────────────────────────────────────────────
  // Four bonded atoms at tetrahedral corners. e.g. CH4
  "Tetrahedral": {
    atoms: [
      { x:  0,     y:  0,     z:  0,    type: 'central' },
      { x:  1.2,   y:  1.2,   z:  1.2,  type: 'bonded'  },
      { x: -1.2,   y: -1.2,   z:  1.2,  type: 'bonded'  },
      { x: -1.2,   y:  1.2,   z: -1.2,  type: 'bonded'  },
      { x:  1.2,   y: -1.2,   z: -1.2,  type: 'bonded'  },
    ],
    bonds: [[0,1],[0,2],[0,3],[0,4]],
  },

  // ── Trigonal Pyramidal (~107°) ────────────────────────────────────────────
  // Three bonded atoms + one lone pair (pushed up). e.g. NH3
  "Trigonal Pyramidal": {
    atoms: [
      { x:  0,     y:  0,    z:  0,     type: 'central' },
      { x:  1.4,   y: -0.5,  z:  0,     type: 'bonded'  },
      { x: -0.7,   y: -0.5,  z:  1.212, type: 'bonded'  },
      { x: -0.7,   y: -0.5,  z: -1.212, type: 'bonded'  },
      { x:  0,     y:  1.5,  z:  0,     type: 'lone'    }, // lone pair above
    ],
    bonds: [[0,1],[0,2],[0,3]],
  },

  // ── Bent (~104.5°) ────────────────────────────────────────────────────────
  // Two bonded atoms + two lone pairs. e.g. H2O
  "Bent": {
    atoms: [
      { x:  0,     y:  0,    z:  0,     type: 'central' },
      { x:  1.2,   y: -0.8,  z:  0,     type: 'bonded'  },
      { x: -1.2,   y: -0.8,  z:  0,     type: 'bonded'  },
      { x:  0.5,   y:  1.2,  z:  0,     type: 'lone'    }, // lone pair 1
      { x: -0.5,   y:  1.2,  z:  0,     type: 'lone'    }, // lone pair 2
    ],
    bonds: [[0,1],[0,2]],
  },

  // ── Trigonal Bipyramidal (90°, 120°) ──────────────────────────────────────
  // 3 equatorial atoms (120° apart in xz-plane) + 2 axial atoms (top/bottom).
  // e.g. PCl5, PF5
  "Trigonal Bipyramidal": {
    atoms: [
      { x:  0,     y:  0,    z:  0,     type: 'central' },
      // equatorial — 120° apart in xz-plane
      { x:  1.6,   y:  0,    z:  0,     type: 'bonded'  },
      { x: -0.8,   y:  0,    z:  1.386, type: 'bonded'  },
      { x: -0.8,   y:  0,    z: -1.386, type: 'bonded'  },
      // axial — top and bottom
      { x:  0,     y:  1.7,  z:  0,     type: 'bonded'  },
      { x:  0,     y: -1.7,  z:  0,     type: 'bonded'  },
    ],
    bonds: [[0,1],[0,2],[0,3],[0,4],[0,5]],
  },

  // ── Seesaw (<90°, <120°) ──────────────────────────────────────────────────
  // 2 axial + 2 equatorial bonded atoms + 1 lone pair in equatorial slot.
  // e.g. SF4, SeF4
  "Seesaw": {
    atoms: [
      { x:  0,     y:  0,    z:  0,     type: 'central' },
      // axial
      { x:  0,     y:  1.7,  z:  0,     type: 'bonded'  },
      { x:  0,     y: -1.7,  z:  0,     type: 'bonded'  },
      // two equatorial bonded atoms
      { x:  1.6,   y:  0,    z:  0,     type: 'bonded'  },
      { x: -0.8,   y:  0,    z: -1.386, type: 'bonded'  },
      // lone pair occupies the remaining equatorial slot
      { x: -0.8,   y:  0,    z:  1.386, type: 'lone'    },
    ],
    bonds: [[0,1],[0,2],[0,3],[0,4]],
  },

  // ── T-shaped (~90°) ───────────────────────────────────────────────────────
  // 2 axial + 1 equatorial bonded atom + 2 lone pairs in equatorial plane.
  // e.g. ClF3, BrF3
  "T-shaped": {
    atoms: [
      { x:  0,     y:  0,    z:  0,     type: 'central' },
      // axial
      { x:  0,     y:  1.7,  z:  0,     type: 'bonded'  },
      { x:  0,     y: -1.7,  z:  0,     type: 'bonded'  },
      // one equatorial bonded atom
      { x:  1.6,   y:  0,    z:  0,     type: 'bonded'  },
      // two lone pairs fill the remaining equatorial positions
      { x: -0.8,   y:  0,    z:  1.2,   type: 'lone'    },
      { x: -0.8,   y:  0,    z: -1.2,   type: 'lone'    },
    ],
    bonds: [[0,1],[0,2],[0,3]],
  },

  // ── Octahedral (90°) ──────────────────────────────────────────────────────
  // 4 atoms in square equatorial plane + 2 axial atoms. e.g. SF6
  "Octahedral": {
    atoms: [
      { x:  0,     y:  0,    z:  0,     type: 'central' },
      // equatorial square
      { x:  1.6,   y:  0,    z:  0,     type: 'bonded'  },
      { x: -1.6,   y:  0,    z:  0,     type: 'bonded'  },
      { x:  0,     y:  0,    z:  1.6,   type: 'bonded'  },
      { x:  0,     y:  0,    z: -1.6,   type: 'bonded'  },
      // axial
      { x:  0,     y:  1.7,  z:  0,     type: 'bonded'  },
      { x:  0,     y: -1.7,  z:  0,     type: 'bonded'  },
    ],
    bonds: [[0,1],[0,2],[0,3],[0,4],[0,5],[0,6]],
  },

  // ── Square Pyramidal (~90°) ───────────────────────────────────────────────
  // 4 atoms in square base + 1 apex atom above + 1 lone pair below.
  // e.g. BrF5, IF5
  "Square Pyramidal": {
    atoms: [
      { x:  0,     y:  0,    z:  0,     type: 'central' },
      // square base
      { x:  1.6,   y:  0,    z:  0,     type: 'bonded'  },
      { x: -1.6,   y:  0,    z:  0,     type: 'bonded'  },
      { x:  0,     y:  0,    z:  1.6,   type: 'bonded'  },
      { x:  0,     y:  0,    z: -1.6,   type: 'bonded'  },
      // apex atom above
      { x:  0,     y:  1.7,  z:  0,     type: 'bonded'  },
      // lone pair below (slightly closer to centre than bond length)
      { x:  0,     y: -1.3,  z:  0,     type: 'lone'    },
    ],
    bonds: [[0,1],[0,2],[0,3],[0,4],[0,5]],
  },

  // ── Square Planar (90°) ───────────────────────────────────────────────────
  // 4 atoms in square equatorial plane + 2 lone pairs axially above/below.
  // e.g. XeF4, ICl4-
  "Square Planar": {
    atoms: [
      { x:  0,     y:  0,    z:  0,     type: 'central' },
      // square plane
      { x:  1.6,   y:  0,    z:  0,     type: 'bonded'  },
      { x: -1.6,   y:  0,    z:  0,     type: 'bonded'  },
      { x:  0,     y:  0,    z:  1.6,   type: 'bonded'  },
      { x:  0,     y:  0,    z: -1.6,   type: 'bonded'  },
      // lone pairs axially above and below
      { x:  0,     y:  1.3,  z:  0,     type: 'lone'    },
      { x:  0,     y: -1.3,  z:  0,     type: 'lone'    },
    ],
    bonds: [[0,1],[0,2],[0,3],[0,4]],
  },
};

// ══════════════════════════════════════════════════════════════════════════════
// § 2 — THREE.JS 3D VIEWER
// ══════════════════════════════════════════════════════════════════════════════

// Atom appearance config
const ATOM_CONFIG = {
  central: { color: 0x14b8a6, radius: 0.38, opacity: 1.0 },
  bonded:  { color: 0xf59e0b, radius: 0.28, opacity: 1.0 },
  lone:    { color: 0x94a3b8, radius: 0.22, opacity: 0.40 },
};

const BOND_COLOR    = 0xd1fae5;
const BOND_RADIUS   = 0.07;

// Three.js globals — persisted across calls to avoid re-creating the renderer
let renderer, scene, camera, animFrameId;
let isDragging = false, prevMouse = { x: 0, y: 0 };
let pivotGroup; // the group we rotate on drag

/**
 * initViewer()
 * Sets up the Three.js renderer, camera, and lights once.
 * Safe to call multiple times — skips init if already done.
 */
function initViewer() {
  if (renderer) return; // already initialized

  const canvas = document.getElementById('mol-canvas');
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setClearColor(0x000000, 0); // transparent — background set in CSS

  // Camera
  camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.set(0, 0, 8);

  // Lights
  const ambient = new THREE.AmbientLight(0xffffff, 0.55);
  const point1  = new THREE.PointLight(0xffffff, 1.0);
  point1.position.set(5, 8, 5);
  const point2  = new THREE.PointLight(0x99f6e4, 0.4);
  point2.position.set(-5, -3, -5);

  scene = new THREE.Scene();
  scene.add(ambient, point1, point2);

  // Resize handling
  resizeRenderer();
  window.addEventListener('resize', resizeRenderer);

  // Mouse drag to rotate
  canvas.addEventListener('mousedown',  onMouseDown);
  canvas.addEventListener('mousemove',  onMouseMove);
  canvas.addEventListener('mouseup',    () => { isDragging = false; });
  canvas.addEventListener('mouseleave', () => { isDragging = false; });

  // Touch drag for mobile
  canvas.addEventListener('touchstart', onTouchStart, { passive: true });
  canvas.addEventListener('touchmove',  onTouchMove,  { passive: true });

  // Scroll / pinch to zoom
  canvas.addEventListener('wheel', onWheel, { passive: true });
}

function resizeRenderer() {
  const canvas = document.getElementById('mol-canvas');
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}

// ── Mouse / Touch controls ─────────────────────────────────────────────────
function onMouseDown(e) { isDragging = true; prevMouse = { x: e.clientX, y: e.clientY }; }
function onMouseMove(e) {
  if (!isDragging || !pivotGroup) return;
  const dx = e.clientX - prevMouse.x;
  const dy = e.clientY - prevMouse.y;
  pivotGroup.rotation.y += dx * 0.012;
  pivotGroup.rotation.x += dy * 0.012;
  prevMouse = { x: e.clientX, y: e.clientY };
}
function onTouchStart(e) { if (e.touches.length === 1) prevMouse = { x: e.touches[0].clientX, y: e.touches[0].clientY }; }
function onTouchMove(e) {
  if (e.touches.length !== 1 || !pivotGroup) return;
  const dx = e.touches[0].clientX - prevMouse.x;
  const dy = e.touches[0].clientY - prevMouse.y;
  pivotGroup.rotation.y += dx * 0.012;
  pivotGroup.rotation.x += dy * 0.012;
  prevMouse = { x: e.touches[0].clientX, y: e.touches[0].clientY };
}
function onWheel(e) {
  camera.position.z = Math.max(3, Math.min(16, camera.position.z + e.deltaY * 0.01));
}

// ── Scene building helpers ─────────────────────────────────────────────────

/** Create a sphere mesh for one atom */
function makeSphere(x, y, z, type) {
  const cfg  = ATOM_CONFIG[type];
  const geo  = new THREE.SphereGeometry(cfg.radius, 32, 32);
  const mat  = new THREE.MeshPhongMaterial({
    color:       cfg.color,
    transparent: cfg.opacity < 1,
    opacity:     cfg.opacity,
    shininess:   90,
    specular:    0x334155,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(x, y, z);
  return mesh;
}

/** Create a cylinder between two atom positions (the bond) */
function makeBond(a, b) {
  const start = new THREE.Vector3(a.x, a.y, a.z);
  const end   = new THREE.Vector3(b.x, b.y, b.z);
  const dir   = new THREE.Vector3().subVectors(end, start);
  const len   = dir.length();

  const geo   = new THREE.CylinderGeometry(BOND_RADIUS, BOND_RADIUS, len, 16);
  const mat   = new THREE.MeshPhongMaterial({ color: BOND_COLOR, shininess: 60 });
  const mesh  = new THREE.Mesh(geo, mat);

  // Position cylinder at midpoint, orient along bond direction
  mesh.position.copy(start).addScaledVector(dir, 0.5);
  mesh.quaternion.setFromUnitVectors(
    new THREE.Vector3(0, 1, 0),
    dir.clone().normalize()
  );
  return mesh;
}

/**
 * loadScene(geometryName)
 * Clears the current scene objects and populates it with the
 * pre-defined structure for the given geometry name.
 * Called once per prediction — no geometry is re-generated.
 */
function loadScene(geometryName) {
  initViewer();

  // Remove old molecule group and free GPU memory if present
  if (pivotGroup) {
    pivotGroup.children.forEach(mesh => {
      if (mesh.geometry) mesh.geometry.dispose();
      if (mesh.material) {
        if (Array.isArray(mesh.material)) {
          mesh.material.forEach(m => m.dispose());
        } else {
          mesh.material.dispose();
        }
      }
    });
    scene.remove(pivotGroup);
  }

  const def = GEOMETRY_SCENES[geometryName];
  if (!def) return; // unknown geometry — viewer stays empty

  pivotGroup = new THREE.Group();

  // Add atoms
  def.atoms.forEach(a => pivotGroup.add(makeSphere(a.x, a.y, a.z, a.type)));

  // Add bonds
  def.bonds.forEach(([i, j]) => {
    pivotGroup.add(makeBond(def.atoms[i], def.atoms[j]));
  });

  // Gentle initial tilt so structure reads as 3D immediately
  pivotGroup.rotation.x = 0.3;
  pivotGroup.rotation.y = 0.4;

  scene.add(pivotGroup);

  // Cancel any existing render loop, start fresh
  if (animFrameId) cancelAnimationFrame(animFrameId);
  renderLoop();
}

/** Render loop — slow auto-rotate when user isn't dragging */
function renderLoop() {
  animFrameId = requestAnimationFrame(renderLoop);
  if (!isDragging && pivotGroup) pivotGroup.rotation.y += 0.004;
  renderer.render(scene, camera);
}

// ══════════════════════════════════════════════════════════════════════════════
// § 3 — MODE SWITCHING
// ══════════════════════════════════════════════════════════════════════════════

let currentMode = 'molecule'; // 'molecule' | 'manual'

/**
 * switchMode(mode)
 * Shows the correct input section and highlights the active button.
 */
function switchMode(mode) {
  currentMode = mode;
  document.getElementById('btn-molecule').classList.toggle('active', mode === 'molecule');
  document.getElementById('btn-manual').classList.toggle('active', mode === 'manual');
  document.getElementById('section-molecule').classList.toggle('hidden', mode !== 'molecule');
  document.getElementById('section-manual').classList.toggle('hidden', mode !== 'manual');
  hideError();
  hideResult();
}

// ══════════════════════════════════════════════════════════════════════════════
// § 4 — PREDICT (API CALL)
// ══════════════════════════════════════════════════════════════════════════════

async function predict() {
  hideError();
  hideResult();

  let payload;

  if (currentMode === 'molecule') {
    const mol = document.getElementById('molecule-input').value.trim();
    if (!mol) { showError('Please enter a molecule formula.'); return; }
    payload = { mode: 'molecule', molecule: mol };
  } else {
    const bp = document.getElementById('bond-pairs').value.trim();
    const lp = document.getElementById('lone-pairs').value.trim();
    if (bp === '' || lp === '') { showError('Please enter both bond pairs and lone pairs.'); return; }
    payload = { mode: 'manual', bond_pairs: Number(bp), lone_pairs: Number(lp) };
  }

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (data.error) {
      showError(data.error);
      // Molecule not found → auto-switch to manual mode
      if (response.status === 404) setTimeout(() => switchMode('manual'), 600);
      return;
    }

    renderResult(data);

  } catch (err) {
    showError('Could not reach the server. Is Flask running?');
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// § 5 — RENDER RESULT + 3D VIEWER
// ══════════════════════════════════════════════════════════════════════════════

function renderResult(data) {
  // Populate data cards
  document.getElementById('res-geometry').textContent = data.geometry;
  document.getElementById('res-angle').textContent    = data.angle;
  document.getElementById('res-hybrid').textContent   = data.hybridization;
  document.getElementById('res-bp').textContent       = data.bond_pairs;
  document.getElementById('res-lp').textContent       = data.lone_pairs;

  // Show result card with animation
  const card = document.getElementById('result-card');
  card.classList.remove('hidden');
  card.style.animation = 'none'; void card.offsetWidth; card.style.animation = '';

  // Show 3D viewer card and load the matching pre-defined scene
  const viewerCard = document.getElementById('viewer-card');
  viewerCard.classList.remove('hidden');
  viewerCard.style.animation = 'none'; void viewerCard.offsetWidth; viewerCard.style.animation = '';

  // loadScene picks the correct hardcoded geometry — nothing is generated
  loadScene(data.geometry);

  // Scroll viewer into view smoothly
  setTimeout(() => viewerCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 100);
}

function hideResult() {
  document.getElementById('result-card').classList.add('hidden');
  document.getElementById('viewer-card').classList.add('hidden');
}

// ── Error helpers ──────────────────────────────────────────────────────────
function showError(msg) {
  const box = document.getElementById('error-box');
  document.getElementById('error-text').textContent = msg;
  box.classList.remove('hidden');
  box.style.animation = 'none'; void box.offsetWidth; box.style.animation = '';
}
function hideError() {
  document.getElementById('error-box').classList.add('hidden');
}

// ── Enter key shortcut ─────────────────────────────────────────────────────
document.addEventListener('keydown', (e) => { if (e.key === 'Enter') predict(); });
