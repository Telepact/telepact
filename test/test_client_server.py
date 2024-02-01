from test.util import verify_server_case, verify_flat_case, verify_client_case, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c
import asyncio
import pytest
import time
import importlib
import json
from copy import deepcopy as dc

@pytest.fixture(scope="module")
def client_server_proc(loop, nats_client, dispatcher_server):
    lib_name = dispatcher_server

    init_topics = ['client-frontdoor', 'client-backdoor', 'frontdoor', 'backdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'client-server', t) for t in init_topics)     

    cserver_id = '{}.{}'.format(lib_name, 'client-server-client')
    server_id = '{}.{}'.format(lib_name, 'client-server-server')

    async def t():
        req = json.dumps([{}, {'StartServer': {'id': server_id, 'apiSchemaPath': c.example_api_path, 'frontdoorTopic': topics[2], 'backdoorTopic': topics[3]}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)
        req2 = json.dumps([{}, {'StartClientServer': {'id': cserver_id, 'clientFrontdoorTopic': topics[0], 'clientBackdoorTopic': topics[1]}}])
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

    print('client_server_proc stopped')

def test_client_server_case(loop, client_server_proc, nats_client, name, req, res):
    topics = client_server_proc

    async def t():
        await verify_client_case(nats_client, dc(req), dc(res), *topics)
                                             
    loop.run_until_complete(t())