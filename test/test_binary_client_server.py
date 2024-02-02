from test.util import verify_client_case, ping_req, startup_check, Constants as c
import pytest
import json
from copy import deepcopy as dc

@pytest.fixture(scope="module")
def binary_client_server_proc(loop, nats_client, dispatcher_server):
    lib_name = dispatcher_server

    init_topics = ['client-frontdoor', 'client-backdoor', 'frontdoor', 'backdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'binary-client-server', t) for t in init_topics)    

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

    try:
        async def warmup():
            request = [{}, {'fn._ping': {}}]
            await verify_client_case(nats_client, request, None, *topics)

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

    print('binary_client_server_proc stopped')
    
def test_binary_client_server_case(loop, binary_client_server_proc, nats_client, name, req, res):
    topics = binary_client_server_proc

    async def t():
        await verify_client_case(nats_client, dc(req), dc(res), *topics, assert_binary=True)
                                                 
    loop.run_until_complete(t())


def test_pbinary_client_server_case(loop, binary_client_server_proc, nats_client, name, req, res):
    topics = binary_client_server_proc

    req[0]['_pac'] = True

    async def t():
        await verify_client_case(nats_client, dc(req), dc(res), *topics, assert_binary=True)
                                                 
    loop.run_until_complete(t())