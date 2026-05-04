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
import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

import nats
from nats.aio.client import Client as NatsClient
from nats.errors import TimeoutError as NatsTimeoutError

EXAMPLE_DIR = Path(__file__).resolve().parent.parent
CLIENT_DIST_DIR = EXAMPLE_DIR / 'client' / 'dist'
BODY_LIMIT_BYTES = 64 * 1024
STATIC_CONTENT_TYPES = {
    '.css': 'text/css; charset=utf-8',
    '.html': 'text/html; charset=utf-8',
    '.ico': 'image/x-icon',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.svg': 'image/svg+xml',
}


class ProxyTransportError(Exception):
    def __init__(self, message: str, *, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class NatsProxy:
    def __init__(self, nats_url: str, timeout_seconds: float) -> None:
        self._nats_url = nats_url
        self._timeout_seconds = timeout_seconds
        self._loop = asyncio.new_event_loop()
        self._client: NatsClient | None = None
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _connect_with_retry(self, timeout_seconds: float) -> None:
        deadline = self._loop.time() + timeout_seconds
        while True:
            try:
                self._client = await nats.connect(self._nats_url, name='telepact-full-stack-proxy')
                return
            except Exception:
                if self._loop.time() >= deadline:
                    raise
                await asyncio.sleep(0.1)

    def connect(self, timeout_seconds: float = 10.0) -> None:
        future = asyncio.run_coroutine_threadsafe(self._connect_with_retry(timeout_seconds), self._loop)
        future.result(timeout=timeout_seconds + 1)

    async def _request(self, subject: str, payload: bytes) -> bytes:
        if self._client is None or self._client.is_closed:
            raise ProxyTransportError('NATS connection is not available', status_code=503)
        message = await self._client.request(subject, payload, timeout=self._timeout_seconds)
        return bytes(message.data)

    def request(self, subject: str, payload: bytes) -> bytes:
        future = asyncio.run_coroutine_threadsafe(self._request(subject, payload), self._loop)
        try:
            return future.result(timeout=self._timeout_seconds + 1)
        except NatsTimeoutError as error:
            raise ProxyTransportError(f'NATS request timed out for {subject}', status_code=504) from error
        except ProxyTransportError:
            raise
        except Exception as error:
            raise ProxyTransportError(f'NATS request failed for {subject}: {error}', status_code=502) from error

    async def _close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.close()
        self._loop.stop()

    def close(self) -> None:
        future = asyncio.run_coroutine_threadsafe(self._close(), self._loop)
        future.result(timeout=5)
        self._thread.join(timeout=5)

    def is_connected(self) -> bool:
        client = self._client
        return client is not None and client.is_connected and not client.is_closed

    @property
    def nats_url(self) -> str:
        return self._nats_url


NATS_PROXY: NatsProxy | None = None


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
    handler.send_header('Content-Type', content_type)
    handler.send_header('Content-Length', str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _proxy() -> NatsProxy:
    if NATS_PROXY is None:
        raise RuntimeError('proxy not initialized')
    return NATS_PROXY


def _read_request_bytes(handler: BaseHTTPRequestHandler) -> bytes:
    content_length = int(handler.headers.get('Content-Length', '0'))
    if content_length > BODY_LIMIT_BYTES:
        raise ProxyTransportError('request body too large', status_code=413)
    return handler.rfile.read(content_length)


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == '/healthz':
            proxy = _proxy()
            status_code = 200 if proxy.is_connected() else 503
            _write_json(self, {'ok': proxy.is_connected(), 'natsUrl': proxy.nats_url}, status_code=status_code)
            return
        _serve_static(self, self.path)

    def do_POST(self) -> None:
        request_path = urlsplit(self.path).path
        if not request_path.startswith('/rpc/'):
            self.send_response(404)
            self.end_headers()
            return

        subject = unquote(request_path.removeprefix('/rpc/')).strip()
        if not subject:
            _write_json(self, {'error': 'missing NATS subject in URL'}, status_code=400)
            return

        try:
            request_bytes = _read_request_bytes(self)
            response_bytes = _proxy().request(subject, request_bytes)
        except ProxyTransportError as error:
            _write_json(self, {'error': str(error), 'subject': subject}, status_code=error.status_code)
            return

        self.send_response(200)
        self.send_header('Content-Type', 'application/octet-stream')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.send_header('X-NATS-Subject', subject)
        self.end_headers()
        self.wfile.write(response_bytes)

    def log_message(self, format_string: str, *args: object) -> None:
        return


def create_http_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), RequestHandler)


def main() -> None:
    parser = argparse.ArgumentParser(description='Run the full-stack proxy example HTTP server.')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--nats-url', default='nats://127.0.0.1:4222')
    parser.add_argument('--nats-timeout-seconds', type=float, default=2.0)
    args = parser.parse_args()

    global NATS_PROXY
    NATS_PROXY = NatsProxy(args.nats_url, args.nats_timeout_seconds)
    NATS_PROXY.connect()

    server = create_http_server(args.host, args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if NATS_PROXY is not None:
            NATS_PROXY.close()


if __name__ == '__main__':
    main()
