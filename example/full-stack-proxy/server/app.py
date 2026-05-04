#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from __future__ import annotations

import argparse
import json
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from telepact_app import TelepactNatsBridge, log, snapshot_ops_state

EXAMPLE_DIR = Path(__file__).resolve().parent.parent
CLIENT_DIST_DIR = EXAMPLE_DIR / 'client' / 'dist'
STATIC_CONTENT_TYPES = {
    '.css': 'text/css; charset=utf-8',
    '.html': 'text/html; charset=utf-8',
    '.ico': 'image/x-icon',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.svg': 'image/svg+xml',
}


def _set_json_headers(handler: BaseHTTPRequestHandler, status_code: int = 200) -> None:
    handler.send_response(status_code)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Cache-Control', 'no-store')


def _write_json(handler: BaseHTTPRequestHandler, payload: dict[str, object], status_code: int = 200) -> None:
    encoded = json.dumps(payload).encode('utf-8')
    _set_json_headers(handler, status_code)
    handler.send_header('Content-Length', str(len(encoded)))
    handler.end_headers()
    handler.wfile.write(encoded)


def _safe_static_path(url_path: str) -> Path | None:
    client_root = CLIENT_DIST_DIR.resolve()
    requested_path = unquote(urlsplit(url_path).path)
    requested = PurePosixPath('index.html' if requested_path in ('', '/') else requested_path.lstrip('/'))
    if requested.is_absolute() or '..' in requested.parts:
        return None

    candidate = (client_root / Path(*requested.parts)).resolve()
    if candidate.exists() and candidate.is_file() and client_root in candidate.parents:
        return candidate

    fallback = (client_root / 'index.html').resolve()
    if requested.suffix == '' and fallback.exists() and client_root in fallback.parents:
        return fallback
    return None


def _serve_static(handler: BaseHTTPRequestHandler, url_path: str) -> None:
    file_path = _safe_static_path(url_path)
    if file_path is None or not file_path.is_file():
        handler.send_response(404)
        handler.end_headers()
        return

    data = file_path.read_bytes()
    content_type = STATIC_CONTENT_TYPES.get(file_path.suffix, 'application/octet-stream')
    handler.send_response(200)
    handler.send_header('Content-Type', content_type or 'application/octet-stream')
    handler.send_header('Content-Length', str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _set_session_cookie(handler: BaseHTTPRequestHandler, session_token: str | None) -> None:
    cookie = SimpleCookie()
    cookie['session'] = '' if session_token is None else session_token
    cookie['session']['path'] = '/'
    cookie['session']['httponly'] = True
    cookie['session']['samesite'] = 'Lax'
    if session_token is None:
        cookie['session']['max-age'] = 0
    handler.send_header('Set-Cookie', cookie.output(header='').strip())


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == '/healthz':
            _write_json(self, {'ok': True})
            return
        if self.path == '/ops/snapshot':
            _write_json(self, snapshot_ops_state())
            return
        _serve_static(self, self.path)

    def do_POST(self) -> None:
        if self.path == '/session/user':
            payload = {'session': 'reader', 'cookie': 'demo-user-session'}
            _set_json_headers(self)
            _set_session_cookie(self, 'demo-user-session')
            body = json.dumps(payload).encode('utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == '/session/admin':
            payload = {'session': 'admin', 'cookie': 'demo-admin-session'}
            _set_json_headers(self)
            _set_session_cookie(self, 'demo-admin-session')
            body = json.dumps(payload).encode('utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == '/session/logout':
            payload = {'session': 'anonymous'}
            _set_json_headers(self)
            _set_session_cookie(self, None)
            body = json.dumps(payload).encode('utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format_string: str, *args: object) -> None:
        return


def create_http_server(host: str = '127.0.0.1', port: int = 8000) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), RequestHandler)


def main() -> None:
    parser = argparse.ArgumentParser(description='Run the Telepact full-stack proxy example server.')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--nats-url', default='nats://127.0.0.1:4222')
    parser.add_argument('--topic', default='example.full-stack-proxy.telepact')
    args = parser.parse_args()

    bridge = TelepactNatsBridge(args.nats_url, args.topic)
    bridge.start()
    server = create_http_server(args.host, args.port)
    log.info('serving full-stack proxy example on http://%s:%s', args.host, args.port)
    log.info('listening for Telepact requests on %s via %s', args.nats_url, args.topic)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        bridge.close()


if __name__ == '__main__':
    main()
