#!/usr/bin/env python3
"""Small HTTP(S) proxy that blocks high-risk GitHub solution-leakage hosts.

This proxy is intentionally conservative.  For HTTPS CONNECT requests a proxy
can see the hostname but not the path without MITM, so it blocks the GitHub hosts
that expose task repositories, PR diffs, raw files, and archive downloads.  Use
it during benchmark agent runs together with:

    DEPBENCH_AGENT_PROXY_URL=http://172.100.216.1:18080
    python _run_configs/patch_harbor_agent_proxy_env.py

The existing shell-level task-repo blocker still does exact owner/repo matching
for git/curl/wget/gh command arguments; this proxy catches clients that honor
HTTP(S)_PROXY but do not go through those wrappers.
"""

from __future__ import annotations

import argparse
import select
import socket
import socketserver
import urllib.parse
from http.server import BaseHTTPRequestHandler


BLOCKED_HOSTS = {
    "github.com",
    "www.github.com",
    "api.github.com",
    "raw.githubusercontent.com",
    "codeload.github.com",
    "patch-diff.githubusercontent.com",
}


class ProxyHandler(BaseHTTPRequestHandler):
    timeout = 30

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.client_address[0]} - {fmt % args}", flush=True)

    @staticmethod
    def _host_only(value: str) -> str:
        value = value.lower().strip()
        if value.startswith("["):
            return value.split("]", 1)[0].strip("[]")
        return value.split(":", 1)[0]

    def _blocked(self, host: str) -> bool:
        return self._host_only(host) in BLOCKED_HOSTS

    def _send_blocked(self, host: str) -> None:
        self.send_response(451, "DepBench task-repo egress blocked")
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(
            (
                "DepBench policy: GitHub task-repository/PR access is blocked "
                f"during agent solving ({host}).\n"
            ).encode()
        )

    def do_CONNECT(self) -> None:
        host_port = self.path
        host = self._host_only(host_port)
        if self._blocked(host):
            self._send_blocked(host)
            return
        port = 443
        if ":" in host_port.rsplit("]", 1)[-1]:
            try:
                port = int(host_port.rsplit(":", 1)[1])
            except ValueError:
                port = 443
        try:
            upstream = socket.create_connection((host, port), timeout=self.timeout)
        except OSError as exc:
            self.send_error(502, str(exc))
            return
        self.send_response(200, "Connection Established")
        self.end_headers()
        self._tunnel(upstream)

    def do_GET(self) -> None:
        self._proxy_http()

    def do_POST(self) -> None:
        self._proxy_http()

    def do_PUT(self) -> None:
        self._proxy_http()

    def do_PATCH(self) -> None:
        self._proxy_http()

    def do_DELETE(self) -> None:
        self._proxy_http()

    def do_HEAD(self) -> None:
        self._proxy_http()

    def _proxy_http(self) -> None:
        parsed = urllib.parse.urlsplit(self.path)
        host = parsed.hostname or self.headers.get("Host", "")
        if self._blocked(host):
            self._send_blocked(host)
            return
        if not parsed.scheme or not parsed.netloc:
            self.send_error(400, "Expected absolute proxy URL")
            return
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        target = parsed.hostname
        if target is None:
            self.send_error(400, "Missing target host")
            return
        path = urllib.parse.urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
        body_len = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(body_len) if body_len else b""
        try:
            upstream = socket.create_connection((target, port), timeout=self.timeout)
            request_line = f"{self.command} {path} {self.request_version}\r\n".encode()
            upstream.sendall(request_line)
            for key, value in self.headers.items():
                if key.lower() in {"proxy-connection", "connection"}:
                    continue
                upstream.sendall(f"{key}: {value}\r\n".encode())
            upstream.sendall(b"Connection: close\r\n\r\n")
            if body:
                upstream.sendall(body)
            while True:
                chunk = upstream.recv(65536)
                if not chunk:
                    break
                self.wfile.write(chunk)
        except OSError as exc:
            self.send_error(502, str(exc))
        finally:
            try:
                upstream.close()
            except Exception:
                pass

    def _tunnel(self, upstream: socket.socket) -> None:
        sockets = [self.connection, upstream]
        try:
            while True:
                readable, _, errored = select.select(sockets, [], sockets, self.timeout)
                if errored or not readable:
                    break
                for sock in readable:
                    other = upstream if sock is self.connection else self.connection
                    data = sock.recv(65536)
                    if not data:
                        return
                    other.sendall(data)
        finally:
            upstream.close()


class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=18080)
    args = parser.parse_args()
    with ThreadingHTTPServer((args.host, args.port), ProxyHandler) as server:
        print(f"DepBench GitHub guard proxy listening on {args.host}:{args.port}", flush=True)
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
