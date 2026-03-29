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


def post(url: str, numerator: int, denominator: int) -> list[object]:
    body = [
        {},
        {
            'fn.divide': {
                'numerator': numerator,
                'denominator': denominator,
            },
        },
    ]

    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode('utf-8'))


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('usage: python check.py <url>')

    success = post(sys.argv[1], 8, 2)
    if success[1].get('Ok_', {}).get('quotient') != 4:
        raise SystemExit(f'unexpected success response: {success!r}')

    failure = post(sys.argv[1], 8, 0)
    if failure[1].get('ErrorCannotDivideByZero', {}).get('denominator') != 0:
        raise SystemExit(f'unexpected failure response: {failure!r}')

    print('py-errors check passed')


if __name__ == '__main__':
    main()
