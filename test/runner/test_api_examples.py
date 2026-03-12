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

import pytest

from util import send_case, startup_check, verify_flat_case, verify_server_case, ping_req, Constants as c


def _find_definition(api: list[object], schema_key: str) -> dict[str, object]:
    for definition in api:
        definition_map = dict(definition)
        if schema_key in definition_map:
            return definition_map
    raise AssertionError(f'Missing schema entry: {schema_key}')


@pytest.fixture(scope="module")
def api_examples_auth_server_proc(loop, nats_client, dispatcher_server):
    lib_name = dispatcher_server

    init_topics = ['frontdoor', 'backdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'api-examples-auth', t) for t in init_topics)

    server_id = '{}.{}'.format(lib_name, 'api-examples-auth')

    async def t():
        req = json.dumps([{}, {'StartServer': {'id': server_id, 'apiSchemaPath': c.auth_api_path,
                         'frontdoorTopic': topics[0], 'backdoorTopic': topics[1], 'authRequired': True}}])
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
        await nats_client.request(lib_name, req.encode(), timeout=5)

    loop.run_until_complete(t2())


@pytest.fixture(scope="module")
def api_examples_mock_server_proc(loop, nats_client, dispatcher_server):
    lib_name = dispatcher_server

    topics = ('{}.{}.{}'.format(lib_name, 'api-examples-mock', 'frontdoor'),)

    server_id = '{}.{}'.format(lib_name, 'api-examples-mock')

    async def t():
        req = json.dumps([{}, {'StartMockServer': {
                         'id': server_id, 'apiSchemaPath': c.example_api_path, 'frontdoorTopic': topics[0]}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t())

    try:
        startup_check(loop, lambda: verify_flat_case(
            nats_client, ping_req, None, *topics))
    except Exception:
        raise

    yield topics

    async def t2():
        req = json.dumps([{}, {'Stop': {'id': server_id}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t2())


def test_api_examples_auth(loop, api_examples_auth_server_proc, nats_client):
    frontdoor_topic = api_examples_auth_server_proc[0]

    async def t():
        response = await send_case(
            nats_client,
            [{}, {'fn.api_': {'includeExamples!': True}}],
            None,
            frontdoor_topic,
        )
        api = response[1]['Ok_']['api']

        assert [next(key for key in definition if key not in {'///', '->', '_errors', 'example', 'inputExample', 'outputExample'}) for definition in api] == [
            'info.AuthExample',
            'errors.Auth_',
            'fn.test',
            'headers.Auth_',
            'struct.Auth_',
        ]

        assert _find_definition(api, 'info.AuthExample')['example'] == {}
        assert _find_definition(api, 'errors.Auth_')['example'] == {
            'ErrorUnauthorized_': {
                'message!': 'sigma',
            },
        }
        assert _find_definition(api, 'fn.test')['inputExample'] == {'fn.test': {}}
        assert _find_definition(api, 'fn.test')['outputExample'] == {'Ok_': {}}
        assert _find_definition(api, 'headers.Auth_')['inputExample'] == {
            '@auth_': {
                'token': 'sigma',
            },
        }
        assert _find_definition(api, 'headers.Auth_')['outputExample'] == {}
        assert _find_definition(api, 'struct.Auth_')['example'] == {
            'token': 'sigma',
        }

    loop.run_until_complete(t())


def test_api_examples_mock(loop, api_examples_mock_server_proc, nats_client):
    frontdoor_topic = api_examples_mock_server_proc[0]

    async def t():
        response = await send_case(
            nats_client,
            [{}, {'fn.api_': {'includeInternal!': True, 'includeExamples!': True}}],
            None,
            frontdoor_topic,
        )
        api = response[1]['Ok_']['api']

        stub_definition = _find_definition(api, '_ext.Stub_')
        call_definition = _find_definition(api, '_ext.Call_')
        verify_definition = _find_definition(api, 'fn.verify_')
        value_definition = _find_definition(api, 'struct.Value')

        assert 'https://github.com/telepact/telepact/blob/main/doc/mocking.md' in ' '.join(stub_definition['///'])
        assert 'https://github.com/telepact/telepact/blob/main/doc/mocking.md' in ' '.join(call_definition['///'])

        assert set(stub_definition['example'].keys()) == {'fn.test', '->'}
        assert set(call_definition['example'].keys()) == {'fn.test'}
        assert set(verify_definition['inputExample']['fn.verify_']['call'].keys()) == {'fn.test'}
        assert verify_definition['inputExample']['fn.verify_']['count!'] == {
            'AtLeast': {
                'times': 139347212,
            },
        }
        assert verify_definition['inputExample']['fn.verify_']['strictMatch!'] is False
        assert isinstance(stub_definition['example']['fn.test']['value!']['bytes!'], str)
        assert isinstance(call_definition['example']['fn.test']['value!']['bytes!'], str)
        assert isinstance(verify_definition['inputExample']['fn.verify_']['call']['fn.test']['value!']['bytes!'], str)
        assert isinstance(value_definition['example']['bytes!'], str)
        assert value_definition['example']['bytes!'] == 'RH/hBg=='
        assert value_definition['example']['sel!'] == {}

    loop.run_until_complete(t())
