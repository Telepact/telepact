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
        assert unauthenticated_body['ErrorUnauthenticated_']['message!'] == 'missing or invalid session cookie'

        reader = post_json(url, [
            {},
            {
                'fn.me': {},
            },
        ], headers={'Cookie': 'session=demo-user-session'})
        assert reader[1]['Ok_']['userId'] == 'user-123'
        assert reader[1]['Ok_']['role'] == 'reader'

        unauthorized = post_json(url, [
            {},
            {
                'fn.adminReport': {},
            },
        ], headers={'Cookie': 'session=demo-user-session'})
        assert unauthorized[1]['ErrorUnauthorized_']['message!'] == 'admin role required'

        admin = post_json(url, [
            {},
            {
                'fn.adminReport': {},
            },
        ], headers={'Cookie': 'session=demo-admin-session'})
        assert admin[1]['Ok_']['summary'] == 'secret report for admin-456'
    finally:
        stop_server(server, thread)
