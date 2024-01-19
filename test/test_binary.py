from test.util import verify_server_case, verify_flat_case, verify_client_case, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c, get_lib_modules
import asyncio
import pytest
import time
import importlib
import json


@pytest.fixture(scope="module")
def binary_server_proc(loop, nats_client, dispatcher_server):
    lib_name = dispatcher_server

    init_topics = ['frontdoor', 'backdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'binary-server', t) for t in init_topics)

    server_id = '{}.{}'.format(lib_name, 'binary')

    async def t():
        req = json.dumps([{}, {'StartServer': {'id': server_id, 'apiSchemaPath': c.binary_api_path, 'frontdoorTopic': topics[0], 'backdoorTopic': topics[1]}}])
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

    print('binary_server_proc stopped')

def test_binary_case(loop, binary_server_proc, nats_client, name, req, res):
    topics = binary_server_proc
    
    async def t():
        await verify_server_case(nats_client, req, res, *topics)
    
    loop.run_until_complete(t())