#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from server import create_http_server
from test_support import post_json, run_server, stop_server


def test_cookie_auth_example_runs_end_to_end() -> None:
    server = create_http_server()
    thread = run_server(server)
    try:
        url = f'http://127.0.0.1:{server.server_address[1]}/api/telepact'

        unauthenticated = post_json(url, [
            {},
            {
                'fn.me': {},
            },
        ])
        unauthenticated_body = unauthenticated[1]
        assert 'Ok_' not in unauthenticated_body
        assert any('error' in key.lower() for key in unauthenticated_body)

        authenticated = post_json(url, [
            {},
            {
                'fn.me': {},
            },
        ], headers={'Cookie': 'session=demo-session'})
        assert authenticated[1]['Ok_']['userId'] == 'user-123'
    finally:
        stop_server(server, thread)
