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


INDEX_MESSAGE_HEADER = 0
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
        follow_up_name, follow_up_args = next(iter(next_call.items()))
        follow_up_payload = post_json(url, [
            {},
            {
                follow_up_name: follow_up_args,
            },
        ])

        assert follow_up_name == 'fn.getFollowUp'
        assert follow_up_payload[INDEX_MESSAGE_BODY]['Ok_']['summary'] == 'Followed up on follow-up-1'
    finally:
        stop_server(server, thread)
