#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from server import create_http_server
from test_support import post_json, run_server, stop_server


INDEX_MESSAGE_BODY = 1


def test_links_example_runs_end_to_end() -> None:
    server = create_http_server()
    thread = run_server(server)
    try:
        url = f'http://127.0.0.1:{server.server_address[1]}/api/telepact'
        payload = post_json(url, [
            {},
            {
                'fn.createIssueLink': {
                    'title': 'Ship docs',
                },
            },
        ])

        next_call = payload[INDEX_MESSAGE_BODY]['Ok_']['next!']
        follow_up_payload = post_json(url, [
            {},
            next_call,
        ])

        assert follow_up_payload[INDEX_MESSAGE_BODY]['Ok_']['summary'] == 'Followed up on follow-up-1'
    finally:
        stop_server(server, thread)
