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

from util import verify_client_case, ping_req, startup_check, Constants as c
import pytest
import json
from copy import deepcopy as dc


@pytest.fixture(scope="module")
def load_json_server_proc(loop, nats_client, dispatcher_server):
    lib_name = dispatcher_server

    init_topics = ['client-frontdoor', 'frontdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'load-json', t)
                   for t in init_topics)

    cserver_id = '{}.{}'.format(lib_name, 'load-json-client')
    server_id = '{}.{}'.format(lib_name, 'load-json-server')

    async def t():
        req = json.dumps([{}, {'StartMockServer': {'id': server_id, 'apiSchemaPath': c.load_api_path,
                         'frontdoorTopic': topics[1], 'config!': {'minLength': 500, 'maxLength': 500, 'enableGen': True}}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)
        req2 = json.dumps([{}, {'StartClientServer': {
                          'id': cserver_id, 'clientFrontdoorTopic': topics[0], 'clientBackdoorTopic': topics[1], 'useBinary': False}}])
        await nats_client.request(lib_name, req2.encode(), timeout=1)

    loop.run_until_complete(t())

    try:
        startup_check(loop, lambda: verify_client_case(
            nats_client, ping_req, None, topics[0], None, topics[1], None))
    except Exception:
        raise

    try:
        async def warmup():
            request = [{}, {'fn.ping_': {}}]
            await verify_client_case(nats_client, request, None, topics[0], None, topics[1], None)

        loop.run_until_complete(warmup())
    except Exception:
        raise

    yield topics

    async def t2():
        req = json.dumps([{}, {'Stop': {'id': server_id}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)
        req2 = json.dumps([{}, {'Stop': {'id': cserver_id}}])
        await nats_client.request(lib_name, req2.encode(), timeout=1)

    loop.run_until_complete(t2())

    print('load_json_server_proc stopped')


def test_load_json_case(loop, load_json_server_proc, nats_client):
    topics = load_json_server_proc

    async def t():
        for _ in range(50):
            req = [{}, {'fn.getData': {}}]
            await verify_client_case(nats_client, req, None, topics[0], None, topics[1], None)

    loop.run_until_complete(t())
