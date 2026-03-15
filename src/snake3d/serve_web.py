from __future__ import annotations

import http.server
import socketserver
import webbrowser
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8000
WEB_INDEX_PATH = Path("web") / "index.html"


class Snake3DWebRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str, **kwargs) -> None:
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path in ("/", "/index.html"):
            self.path = "/web/index.html"
        return super().do_GET()


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def main() -> int:
    project_root = Path.cwd()
    index_path = project_root / WEB_INDEX_PATH
    if not index_path.exists():
        print(f"Could not find browser entrypoint at {index_path}.")
        return 1

    handler = lambda *args, **kwargs: Snake3DWebRequestHandler(  # noqa: E731
        *args, directory=str(project_root), **kwargs
    )

    with ReusableTCPServer((HOST, PORT), handler) as server:
        url = f"http://{HOST}:{PORT}/web/index.html"
        print(f"Serving Snake3D web client at {url}")
        print("Press Ctrl+C to stop.")
        try:
            webbrowser.open(url)
        except Exception:
            pass

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down web server.")

    return 0
