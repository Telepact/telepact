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
            '@select_': {
                '->': {
                    'Ok_': ['card', 'item'],
                },
                'struct.ResultCard': ['title'],
                'union.ResultItem': {
                    'Card': [],
                },
            },
        },
        {
            'fn.selectNested': {},
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

    expected = [
        {},
        {
            'Ok_': {
                'card': {'title': 'Ship docs'},
                'item': {'Card': {}},
            },
        },
    ]

    if payload != expected:
        raise SystemExit(f'unexpected response: {payload!r}')

    print('py-select check passed')


if __name__ == '__main__':
    main()
