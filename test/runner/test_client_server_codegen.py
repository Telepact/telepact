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
def client_server_codegen_proc(loop, nats_client, dispatcher_server):
    lib_name = dispatcher_server

    init_topics = ['codegen-client-frontdoor',
                   'codegen-client-backdoor', 'codegen-frontdoor', 'codegen-backdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'client-server', t)
                   for t in init_topics)

    cserver_id = '{}.{}'.format(lib_name, 'codegen-client-server-client')
    server_id = '{}.{}'.format(lib_name, 'codegen-client-server-server')

    async def t():
        req = json.dumps([{}, {'StartServer': {'id': server_id, 'apiSchemaPath': c.example_api_path,
                         'frontdoorTopic': topics[2], 'backdoorTopic': topics[3], 'useCodeGen': True}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)
        req2 = json.dumps([{}, {'StartClientServer': {
                          'id': cserver_id, 'clientFrontdoorTopic': topics[0], 'clientBackdoorTopic': topics[1], 'useCodeGen': True}}])
        await nats_client.request(lib_name, req2.encode(), timeout=1)

    loop.run_until_complete(t())

    try:
        startup_check(loop, lambda: verify_client_case(
            nats_client, ping_req, None, *topics))
    except Exception:
        raise

    yield topics

    async def t2():
        req = json.dumps([{}, {'Stop': {'id': server_id}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)
        req2 = json.dumps([{}, {'Stop': {'id': cserver_id}}])
        await nats_client.request(lib_name, req2.encode(), timeout=1)

    loop.run_until_complete(t2())

    print('client_server_codegen_proc stopped')


def test_client_server_codegen_case(loop, client_server_codegen_proc, nats_client, name, req, res):
    topics = client_server_codegen_proc

    async def t():
        if '@good_' not in req[0]:
            pytest.skip('Only test good cases for codegen')

        expected_response = dc(res)

        expected_headers = expected_response[0]

        expected_headers['@codegenc_'] = True
        expected_headers['@codegens_'] = True

        await verify_client_case(nats_client, dc(req), expected_response, *topics)

    loop.run_until_complete(t())
