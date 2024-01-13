from test.util import verify_server_case, verify_flat_case, verify_client_case, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c, get_lib_modules
import asyncio
import pytest
import time
import importlib
import json


@pytest.fixture(scope="module", params=get_lib_modules())
def cold_binary_client_server_proc(loop, nats_client, dispatcher_server, request):
    lib_name = request.param

    init_topics = ['client-frontdoor', 'client-backdoor', 'frontdoor', 'backdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'cold-binary-client-server', t) for t in init_topics)

    cserver_id = '{}.{}'.format(lib_name, 'binary-client-server-client')
    server_id = '{}.{}'.format(lib_name, 'binary-client-server-server')

    async def t():
        req = json.dumps([{}, {'StartServer': {'id': server_id, 'apiSchemaPath': c.example_api_path, 'frontdoorTopic': topics[2], 'backdoorTopic': topics[3]}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)
        req2 = json.dumps([{}, {'StartClientServer': {'id': cserver_id, 'clientFrontdoorTopic': topics[0], 'clientBackdoorTopic': topics[1], 'useBinary': True}}])
        await nats_client.request(lib_name, req2.encode(), timeout=1)

    loop.run_until_complete(t())    

    try:
        startup_check(loop, lambda: verify_client_case(nats_client, ping_req, None, *topics))
    except Exception:
        raise
                                             
    yield topics
    
    async def t2():
        req = json.dumps([{}, {'Stop': {'id': server_id}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)
        req2 = json.dumps([{}, {'Stop': {'id': cserver_id}}])
        await nats_client.request(lib_name, req2.encode(), timeout=1)

    loop.run_until_complete(t2()) 

    print('cold_binary_client_server_proc stopped')
    
def test_cold_binary_client_server_multi_case(loop, cold_binary_client_server_proc, nats_client, name, statements):
    topics = cold_binary_client_server_proc

    async def t():
        for request, expected_response in statements:
            await verify_client_case(nats_client, request, expected_response, *topics, assert_binary=True)

    loop.run_until_complete(t())
