"""
Molecule3D Desktop
==================
Wraps the existing Flask backend + Jinja2 templates in a native
desktop window via pywebview.  No changes to app.py, index.html,
style.css, or script.js are needed.

Install:
    pip install flask numpy pywebview

Run:
    python main.py
"""

import sys
import threading
import time
import socket

import webview
from app import app as flask_app


# ── Helpers ────────────────────────────────────────────────────────────────

def find_free_port() -> int:
    """Bind to port 0 so the OS picks an available port, then release it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run_flask(port: int) -> None:
    """Run Flask in a daemon thread — dies automatically when the window closes."""
    flask_app.run(
        host="127.0.0.1",
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True,
    )


def wait_for_server(port: int, timeout: float = 10.0) -> bool:
    """Poll until Flask is accepting TCP connections (or timeout)."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.3):
                return True
        except OSError:
            time.sleep(0.05)
    return False


# ── Entry point ────────────────────────────────────────────────────────────

def main() -> None:
    port = find_free_port()

    flask_thread = threading.Thread(target=run_flask, args=(port,), daemon=True)
    flask_thread.start()

    if not wait_for_server(port):
        print(
            f"ERROR: Flask did not start on port {port} within the timeout.",
            file=sys.stderr,
        )
        sys.exit(1)

    url = f"http://127.0.0.1:{port}"

    webview.create_window(
        title="Molecule3D — Bond Angle & Geometry Predictor",
        url=url,
        width=1120,
        height=820,
        min_size=(780, 560),
        resizable=True,
        text_select=True,
    )

    # debug=False keeps the DevTools closed; set True if you need them
    webview.start(debug=False)


if __name__ == "__main__":
    main()
