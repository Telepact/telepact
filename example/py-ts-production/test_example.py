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

import json
import threading
import urllib.request
from http.cookiejar import CookieJar

from server import create_http_server


def run_server(server) -> threading.Thread:
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


def stop_server(server, thread: threading.Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


def build_opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))


def request(opener: urllib.request.OpenerDirector, url: str, *, method: str = 'GET', body: bytes | None = None,
            headers: dict[str, str] | None = None) -> tuple[dict[str, str], bytes]:
    request_obj = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    with opener.open(request_obj) as response:
        return dict(response.headers.items()), response.read()


def telepact_request(opener: urllib.request.OpenerDirector, base_url: str,
                     body: dict[str, object]) -> tuple[dict[str, object], dict[str, object], dict[str, str]]:
    response_headers, response_bytes = request(
        opener,
        f'{base_url}/api/telepact',
        method='POST',
        body=json.dumps([
            {},
            body,
        ]).encode(),
        headers={
            'Content-Type': 'application/json',
        },
    )
    telepact_headers, telepact_body = json.loads(response_bytes.decode())
    return telepact_headers, telepact_body, response_headers


def test_production_example_runs_end_to_end() -> None:
    server = create_http_server()
    thread = run_server(server)
    try:
        base_url = f'http://127.0.0.1:{server.server_address[1]}'
        opener = build_opener()

        _, index_bytes = request(opener, f'{base_url}/')
        index_html = index_bytes.decode()
        assert 'Telepact production example' in index_html

        _, app_bytes = request(opener, f'{base_url}/static/app.js')
        app_js = app_bytes.decode()
        assert 'fn.viewerDashboard' in app_js
        assert 'fn.adminAudit' in app_js

        telepact_headers, telepact_body, http_headers = telepact_request(
            opener,
            base_url,
            {'fn.viewerDashboard': {}},
        )
        assert telepact_headers['@id_'] == http_headers['X-Request-Id']
        assert telepact_body['ErrorUnauthenticated_']['message!'] == 'missing or invalid session cookie'

        request(opener, f'{base_url}/login?role=viewer', method='POST', body=b'')

        telepact_headers, telepact_body, http_headers = telepact_request(
            opener,
            base_url,
            {'fn.viewerDashboard': {}},
        )
        assert telepact_headers['@id_'] == http_headers['X-Request-Id']
        assert telepact_body['Ok_']['viewerId'] == 'user-123'
        assert telepact_body['Ok_']['displayName'] == 'Casey Viewer'
        assert len(telepact_body['Ok_']['notices']) == 2

        _, telepact_body, _ = telepact_request(
            opener,
            base_url,
            {'fn.adminAudit': {}},
        )
        assert telepact_body['ErrorUnauthorized_']['message!'] == 'viewer is authenticated but lacks the admin role'

        request(opener, f'{base_url}/login?role=admin', method='POST', body=b'')
        _, telepact_body, _ = telepact_request(
            opener,
            base_url,
            {'fn.adminAudit': {}},
        )
        assert telepact_body['Ok_']['entries'][0] == 'role-change review queue is empty'

        telepact_headers, telepact_body, _ = telepact_request(
            opener,
            base_url,
            {'fn.debugCrash': {}},
        )
        assert 'ErrorUnknown_' in telepact_body
        crash_request_id = telepact_headers['@id_']

        _, observability_bytes = request(opener, f'{base_url}/ops/observability')
        observability = json.loads(observability_bytes.decode())
        assert observability['metrics']['callsByFunction']['fn.viewerDashboard'] >= 2
        assert observability['metrics']['outcomesByFunction']['fn.adminAudit']['ErrorUnauthorized_'] == 1
        assert observability['metrics']['outcomesByFunction']['fn.debugCrash']['exception'] == 1
        assert any(
            event['requestId'] == crash_request_id
            for event in observability['telepactEvents']
            if event['function'] == 'fn.debugCrash'
        )
        assert any(
            f'demo crash for request {crash_request_id}' in event.get('message', '')
            for event in observability['errorEvents']
        )
    finally:
        stop_server(server, thread)
