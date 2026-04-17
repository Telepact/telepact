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

from copy import deepcopy as dc
import json

import pytest

from util import Constants as c, ping_req, startup_check, verify_server_case


@pytest.fixture(scope="module")
def optional_wire_key_json_proc(loop, nats_client, dispatcher_server):
    lib_name = dispatcher_server

    init_topics = ['frontdoor', 'backdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'optional-wire-key-json', t) for t in init_topics)

    server_id = '{}.{}'.format(lib_name, 'optional-wire-key-json-server')

    async def t():
        req = json.dumps([{}, {'StartServer': {'id': server_id, 'apiSchemaPath': c.example_api_path,
                         'frontdoorTopic': topics[0], 'backdoorTopic': topics[1]}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t())

    try:
        startup_check(loop, lambda: verify_server_case(
            nats_client, ping_req, None, *topics))
    except Exception:
        raise

    yield topics

    async def t2():
        req = json.dumps([{}, {'Stop': {'id': server_id}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t2())


def test_optional_wire_key_hint_json(loop, optional_wire_key_json_proc, nats_client):
    topics = optional_wire_key_json_proc

    req = [{}, {'fn.test': {'value!': {'struct!': {'required': True, 'optional': False}}}}]
    res = [
        {'@assert_': {'setCompare': True}},
        {'ErrorInvalidRequestBody_': {'cases': [
            {'path': ['fn.test', 'value!', 'struct!', 'optional'], 'reason': {'ObjectKeyDisallowed': {}}},
            {'path': ['fn.test', 'value!', 'struct!', 'optional'], 'reason': {'ExtensionValidationFailed': {
                'reason': 'Optional struct fields keep the ! suffix on the wire; prefer generated helpers to set them.',
                'data!': {'receivedKey': 'optional', 'expectedWireKey': 'optional!'},
            }}},
        ]}},
    ]

    async def t():
        await verify_server_case(nats_client, dc(req), dc(res), *topics)

    loop.run_until_complete(t())
