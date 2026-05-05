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


def test_select_example_runs_end_to_end() -> None:
    server = create_http_server()
    thread = run_server(server)
    try:
        url = f'http://127.0.0.1:{server.server_address[1]}/api/telepact'
        full_payload = post_json(url, [
            {},
            {
                'fn.trackPackage': {},
            },
        ])
        selected_payload = post_json(url, [
            {
                '+select_': {
                    '->': {
                        'Ok_': ['package', 'latestEvent'],
                    },
                    'struct.Package': ['trackingId'],
                    'union.DeliveryEvent': {
                        'Dropoff': ['location'],
                    },
                },
            },
            {
                'fn.trackPackage': {},
            },
        ])

        assert full_payload == [
            {},
            {
                'Ok_': {
                    'package': {
                        'trackingId': 'PKG-42',
                        'recipient': 'Ada Lovelace',
                        'city': 'London',
                    },
                    'latestEvent': {
                        'Dropoff': {
                            'location': 'Front desk',
                            'signedBy': 'M. Singh',
                        },
                    },
                    'note': 'Left with building reception.',
                },
            },
        ]
        assert selected_payload == [
            {},
            {
                'Ok_': {
                    'package': {
                        'trackingId': 'PKG-42',
                    },
                    'latestEvent': {
                        'Dropoff': {
                            'location': 'Front desk',
                        },
                    },
                },
            },
        ]
        assert selected_payload != full_payload
    finally:
        stop_server(server, thread)
