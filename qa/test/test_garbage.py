from qa.test.util import verify_server_case, ping_req, startup_check, Constants as c
import pytest
import json
from copy import deepcopy as dc


@pytest.fixture(scope="module")
def garbage_server_proc(loop, nats_client, dispatcher_server):
    lib_name = dispatcher_server

    init_topics = ['frontdoor', 'backdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'garbage-server', t) for t in init_topics)

    server_id = '{}.{}'.format(lib_name, 'garbage')

    async def t():
        req = json.dumps([{}, {'StartServer': {'id': server_id, 'apiSchemaPath': c.example_api_path, 'frontdoorTopic': topics[0], 'backdoorTopic': topics[1]}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t())

    try:
        startup_check(loop, lambda: verify_server_case(nats_client, ping_req, None, *topics))
    except Exception:
        raise    

    yield topics

    async def t2():
        req = json.dumps([{}, {'Stop': {'id': server_id}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t2())    

    print('garbage_server_proc stopped')

def test_garbage_case(loop, garbage_server_proc, nats_client, name, req, res):
    topics = garbage_server_proc
    
    async def t():
        await verify_server_case(nats_client, dc(req), dc(res), *topics, just_send=True)
    
    loop.run_until_complete(t())