#!/usr/bin/env python3
"""Local save server for in-page study-guide editing.

Run once:
  python study-save-server.py

Then open guides at:
  http://localhost:8765/1.1%20Operating%20Systems%20and%20File%20Systems.html

Use Edit terms → type → Save. Writes the .html file on disk.
"""

from __future__ import annotations

import json
import mimetypes
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8765

# Only allow saving HTML files that already live under this project folder.
SAFE_NAME = re.compile(r"^[\w .\-()]+$", re.UNICODE)


def resolve_under_root(rel: str) -> Path | None:
    rel = unquote(rel or "").replace("\\", "/").lstrip("/")
    if not rel or ".." in rel.split("/"):
        return None
    name = Path(rel).name
    if not name.lower().endswith(".html"):
        return None
    if not SAFE_NAME.match(name):
        return None
    target = (ROOT / rel).resolve()
    try:
        target.relative_to(ROOT)
    except ValueError:
        return None
    return target


class Handler(BaseHTTPRequestHandler):
    server_version = "StudySave/1.0"

    def log_message(self, fmt: str, *args) -> None:
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/__ping__":
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return

        rel = unquote(parsed.path.lstrip("/"))
        if not rel:
            rel = "index.html"
        path = (ROOT / rel).resolve()
        try:
            path.relative_to(ROOT)
        except ValueError:
            self.send_error(403)
            return
        if not path.is_file():
            self.send_error(404)
            return

        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/__save__":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            self._json(400, {"error": "Invalid JSON"})
            return

        target = resolve_under_root(payload.get("path", ""))
        html = payload.get("html")
        if not target or not isinstance(html, str) or len(html) < 50:
            self._json(400, {"error": "Bad path or empty HTML"})
            return
        if not target.exists():
            self._json(404, {"error": "File does not exist: " + target.name})
            return

        target.write_text(html, encoding="utf-8", newline="\n")
        self._json(200, {"ok": True, "path": str(target.relative_to(ROOT))})

    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Study save server on http://{HOST}:{PORT}/")
    print(f"Serving: {ROOT}")
    print("Open a guide, click Edit terms, type, then Save.")
    print("Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
