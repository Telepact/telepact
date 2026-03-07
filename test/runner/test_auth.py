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

from util import verify_server_case, ping_req, startup_check, send_case, Constants as c
import pytest
import json
from copy import deepcopy as dc


@pytest.fixture(scope="module")
def auth_server_proc(loop, nats_client, dispatcher_server):
    lib_name = dispatcher_server

    init_topics = ['frontdoor', 'backdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'auth', t) for t in init_topics)

    server_id = '{}.{}'.format(lib_name, 'auth')

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

    print('@auth_server_proc stopped')


def test_auth_case(loop, auth_server_proc, nats_client, name, req, res):
    topics = auth_server_proc

    async def t():
        await verify_server_case(nats_client, dc(req), dc(res), *topics)

    loop.run_until_complete(t())


def test_auth_api_includes_internal_when_requested(loop, auth_server_proc, nats_client):
    topics = auth_server_proc

    async def t():
        response = await send_case(
            nats_client,
            [{}, {'fn.api_': {'includeInternal!': True}}],
            None,
            topics[0],
        )

        api = response[1]['Ok_']['api']
        schema_keys = {
            next(key for key in definition.keys() if key not in {'///', '->', '_errors'})
            for definition in api
            if isinstance(definition, dict)
        }

        assert 'fn.api_' in schema_keys
        assert 'fn.ping_' in schema_keys
        assert 'headers.Auth_' in schema_keys
        assert 'headers.Time_' in schema_keys

    loop.run_until_complete(t())
