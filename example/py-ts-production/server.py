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

import asyncio
import json
import threading
import time
import uuid
from collections import Counter, defaultdict, deque
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from telepact import FunctionRouter, Message, Response, Server, TelepactSchema, TelepactSchemaFiles

ROOT = Path(__file__).resolve().parent
INDEX_HTML = ROOT / 'web' / 'index.html'
APP_JS = ROOT / 'dist-web' / 'app.js'
MAX_REQUEST_BYTES = 64 * 1024

SESSIONS: dict[str, dict[str, str]] = {
    'viewer-session': {
        'viewerId': 'user-123',
        'displayName': 'Casey Viewer',
        'role': 'viewer',
    },
    'admin-session': {
        'viewerId': 'admin-007',
        'displayName': 'Avery Admin',
        'role': 'admin',
    },
}

DASHBOARDS: dict[str, dict[str, Any]] = {
    'user-123': {
        'displayName': 'Casey Viewer',
        'notices': [
            {
                'id': 'deploy',
                'summary': 'Canary deployment remains healthy',
                'severity': 'info',
            },
            {
                'id': 'budget',
                'summary': 'Forecast is within the error budget',
                'severity': 'info',
            },
        ],
    },
    'admin-007': {
        'displayName': 'Avery Admin',
        'notices': [
            {
                'id': 'audit',
                'summary': 'Admin audit queue is empty',
                'severity': 'info',
            },
            {
                'id': 'access',
                'summary': 'Two privileged role reviews remain pending',
                'severity': 'warning',
            },
        ],
    },
}


class DemoObservability:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._transport_events: deque[dict[str, object]] = deque(maxlen=30)
        self._telepact_events: deque[dict[str, object]] = deque(maxlen=30)
        self._error_events: deque[dict[str, object]] = deque(maxlen=30)
        self._calls_by_function: Counter[str] = Counter()
        self._outcomes_by_function: defaultdict[str, Counter[str]] = defaultdict(Counter)
        self._latency_samples_ms: defaultdict[str, list[float]] = defaultdict(list)

    def add_transport_event(self, event: dict[str, object]) -> None:
        with self._lock:
            self._transport_events.append(dict(event))

    def add_telepact_event(self, event: dict[str, object]) -> None:
        with self._lock:
            self._telepact_events.append(dict(event))

    def add_error_event(self, event: dict[str, object]) -> None:
        with self._lock:
            self._error_events.append(dict(event))

    def record_call(self, function_name: str, outcome: str, elapsed_ms: float) -> None:
        with self._lock:
            self._calls_by_function[function_name] += 1
            self._outcomes_by_function[function_name][outcome] += 1
            self._latency_samples_ms[function_name].append(elapsed_ms)

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            average_latency = {
                function_name: round(sum(samples) / len(samples), 2)
                for function_name, samples in self._latency_samples_ms.items()
                if samples
            }
            return {
                'transportEvents': list(self._transport_events),
                'telepactEvents': list(self._telepact_events),
                'errorEvents': list(self._error_events),
                'metrics': {
                    'callsByFunction': dict(self._calls_by_function),
                    'outcomesByFunction': {
                        function_name: dict(counter)
                        for function_name, counter in self._outcomes_by_function.items()
                    },
                    'averageLatencyMsByFunction': average_latency,
                },
            }


observability = DemoObservability()

files = TelepactSchemaFiles(str(ROOT / 'api'))
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
options = Server.Options()


def on_auth(headers: dict[str, object]) -> dict[str, object]:
    auth = headers.get('@auth_')
    session = auth.get('Session') if isinstance(auth, dict) else None
    token = session.get('token') if isinstance(session, dict) else None
    account = SESSIONS.get(token) if isinstance(token, str) else None
    if account is None:
        return {}
    return {
        '@viewerId': account['viewerId'],
        '@viewerRole': account['role'],
    }


def on_error(error: Exception) -> None:
    observability.add_error_event({
        'kind': type(error).__name__,
        'message': str(error),
    })


async def middleware(request_message: Message, function_router: FunctionRouter) -> Message:
    function_name = request_message.get_body_target()
    request_id = str(request_message.headers.get('@id_', 'missing'))
    viewer_id = request_message.headers.get('@viewerId')
    started = time.perf_counter()
    outcome = 'exception'
    observability.add_telepact_event({
        'event': 'start',
        'function': function_name,
        'requestId': request_id,
        'viewerId': viewer_id,
    })
    try:
        response = await function_router.route(request_message)
        outcome = response.get_body_target()
        return response
    except Exception as error:
        observability.add_error_event({
            'kind': 'handler',
            'function': function_name,
            'requestId': request_id,
            'message': str(error),
        })
        raise
    finally:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        observability.record_call(function_name, outcome, elapsed_ms)
        observability.add_telepact_event({
            'event': 'finish',
            'function': function_name,
            'requestId': request_id,
            'viewerId': viewer_id,
            'outcome': outcome,
            'elapsedMs': elapsed_ms,
        })


options.on_auth = on_auth
options.on_error = on_error
options.middleware = middleware


def require_authenticated_viewer(request_message: Message) -> str:
    viewer_id = request_message.headers.get('@viewerId')
    if isinstance(viewer_id, str):
        return viewer_id
    raise PermissionError('missing or invalid session cookie')


async def viewer_dashboard(_function_name: str, request_message: Message) -> Message:
    try:
        viewer_id = require_authenticated_viewer(request_message)
    except PermissionError as error:
        return Message({}, {
            'ErrorUnauthenticated_': {
                'message!': str(error),
            },
        })

    dashboard = DASHBOARDS[viewer_id]
    return Message({}, {
        'Ok_': {
            'viewerId': viewer_id,
            'displayName': dashboard['displayName'],
            'notices': dashboard['notices'],
        },
    })


async def admin_audit(_function_name: str, request_message: Message) -> Message:
    try:
        require_authenticated_viewer(request_message)
    except PermissionError as error:
        return Message({}, {
            'ErrorUnauthenticated_': {
                'message!': str(error),
            },
        })

    if request_message.headers.get('@viewerRole') != 'admin':
        return Message({}, {
            'ErrorUnauthorized_': {
                'message!': 'viewer is authenticated but lacks the admin role',
            },
        })

    return Message({}, {
        'Ok_': {
            'entries': [
                'role-change review queue is empty',
                'incident escalation roster is acknowledged',
            ],
        },
    })


async def debug_crash(_function_name: str, request_message: Message) -> Message:
    request_id = request_message.headers.get('@id_', 'missing')
    raise RuntimeError(f'demo crash for request {request_id}')


function_router = FunctionRouter({
    'fn.viewerDashboard': viewer_dashboard,
    'fn.adminAudit': admin_audit,
    'fn.debugCrash': debug_crash,
})
telepact_server = Server(schema, function_router, options)


def read_session_cookie(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None
    cookie = SimpleCookie()
    cookie.load(cookie_header)
    session = cookie.get('session')
    return session.value if session is not None else None


def sanitize_http_header_value(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    allowed = ''.join(character for character in value if character.isalnum() or character in '-._:')
    if not allowed:
        return None
    return allowed[:128]


def build_request_id(headers: Any) -> str:
    request_id = sanitize_http_header_value(headers.get('X-Request-Id'))
    if request_id is not None:
        return request_id
    return f'req-{uuid.uuid4()}'


def json_response(handler: BaseHTTPRequestHandler, status: HTTPStatus, payload: object, extra_headers: dict[str, str] | None = None) -> None:
    response_bytes = json.dumps(payload, indent=2).encode()
    handler.send_response(status.value)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Content-Length', str(len(response_bytes)))
    if extra_headers is not None:
        for key, value in extra_headers.items():
            handler.send_header(key, value)
    handler.end_headers()
    handler.wfile.write(response_bytes)


def serve_file(handler: BaseHTTPRequestHandler, path: Path, content_type: str) -> None:
    if not path.exists():
        json_response(handler, HTTPStatus.NOT_FOUND, {'message': f'missing file: {path.name}'})
        return
    payload = path.read_bytes()
    handler.send_response(HTTPStatus.OK.value)
    handler.send_header('Content-Type', content_type)
    handler.send_header('Content-Length', str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


def create_http_server(host: str = '127.0.0.1', port: int = 0) -> ThreadingHTTPServer:
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == '/':
                serve_file(self, INDEX_HTML, 'text/html; charset=utf-8')
                return
            if parsed.path == '/static/app.js':
                serve_file(self, APP_JS, 'application/javascript; charset=utf-8')
                return
            if parsed.path == '/ops/observability':
                json_response(self, HTTPStatus.OK, observability.snapshot())
                return
            if parsed.path == '/healthz':
                json_response(self, HTTPStatus.OK, {'status': 'ok'})
                return
            json_response(self, HTTPStatus.NOT_FOUND, {'message': 'not found'})

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            request_id = build_request_id(self.headers)
            if parsed.path == '/login':
                role = parse_qs(parsed.query).get('role', ['viewer'])[0]
                token = 'admin-session' if role == 'admin' else 'viewer-session'
                observability.add_transport_event({
                    'path': parsed.path,
                    'requestId': request_id,
                    'kind': 'session',
                    'role': role,
                })
                self.send_response(HTTPStatus.NO_CONTENT.value)
                self.send_header('Set-Cookie', f'session={token}; HttpOnly; Path=/; SameSite=Lax')
                self.send_header('X-Request-Id', request_id)
                self.end_headers()
                return
            if parsed.path == '/logout':
                self.send_response(HTTPStatus.NO_CONTENT.value)
                self.send_header('Set-Cookie', 'session=deleted; expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; Path=/; SameSite=Lax')
                self.send_header('X-Request-Id', request_id)
                self.end_headers()
                return
            if parsed.path != '/api/telepact':
                json_response(self, HTTPStatus.NOT_FOUND, {'message': 'not found'}, {'X-Request-Id': request_id})
                return

            content_length = int(self.headers.get('Content-Length', '0'))
            if content_length > MAX_REQUEST_BYTES:
                json_response(
                    self,
                    HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    {'message': f'request exceeds {MAX_REQUEST_BYTES} bytes'},
                    {'X-Request-Id': request_id},
                )
                return

            request_bytes = self.rfile.read(content_length)
            session_token = read_session_cookie(self.headers.get('Cookie'))
            observability.add_transport_event({
                'path': parsed.path,
                'requestId': request_id,
                'contentLength': content_length,
                'hasSessionCookie': session_token is not None,
            })

            def update_headers(headers: dict[str, object]) -> None:
                headers['@id_'] = request_id
                if session_token is not None:
                    headers['@auth_'] = {'Session': {'token': session_token}}

            response = asyncio.run(telepact_server.process(request_bytes, update_headers))
            write_telepact_response(self, request_id, response)

        def log_message(self, format_string: str, *args: object) -> None:
            return

    return ThreadingHTTPServer((host, port), RequestHandler)


def write_telepact_response(handler: BaseHTTPRequestHandler, request_id: str, response: Response) -> None:
    content_type = 'application/octet-stream' if '@bin_' in response.headers else 'application/json'
    handler.send_response(HTTPStatus.OK.value)
    handler.send_header('Content-Type', content_type)
    handler.send_header('Content-Length', str(len(response.bytes)))
    handler.send_header('X-Request-Id', request_id)
    handler.end_headers()
    handler.wfile.write(response.bytes)


def main() -> None:
    server = create_http_server(host='127.0.0.1', port=8000)
    host, port = server.server_address
    print(f'Serving production example on http://{host}:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
