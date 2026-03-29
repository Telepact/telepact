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

import json
import sys
import urllib.request


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('usage: python check.py <url>')

    request_body = [
        {
            '@id_': 'trace-123',
        },
        {
            'fn.greet': {
                'subject': 'Telepact',
            },
        },
    ]

    request = urllib.request.Request(
        sys.argv[1],
        data=json.dumps(request_body).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    with urllib.request.urlopen(request) as response:
        payload = json.loads(response.read().decode('utf-8'))

    expected_headers = {
        '@id_': 'trace-123',
        '@warn_': ['header example'],
    }
    expected_body = {
        'Ok_': {
            'message': 'Hello Telepact!',
        },
    }

    if payload != [expected_headers, expected_body]:
        raise SystemExit(f'unexpected response: {payload!r}')

    print('py-headers check passed')


if __name__ == '__main__':
    main()
