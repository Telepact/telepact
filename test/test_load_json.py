from test.util import verify_server_case, verify_flat_case, verify_client_case, get_nats_client, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c, get_lib_modules
import asyncio
import pytest
import time
import os
import importlib
import json

@pytest.fixture(scope="module", params=get_lib_modules())
def load_json_server_proc(loop, nats_server, dispatcher_server, request):
    lib_name = request.param

    init_topics = ['client-frontdoor', 'frontdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'load', t) for t in init_topics)    

    cserver_id = '{}.{}'.format(lib_name, 'load-client')
    server_id = '{}.{}'.format(lib_name, 'load-server')

    async def t():
        nats_client = await get_nats_client()
        req = json.dumps([{}, {'StartMockServer': {'id': server_id, 'apiSchemaPath': c.load_api_path, 'frontdoorTopic': topics[1], 'config': {'minLength': 100, 'maxLength': 150, 'enableGen': True}}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)    
        req2 = json.dumps([{}, {'StartClientServer': {'id': cserver_id, 'clientFrontdoorTopic': topics[0], 'clientBackdoorTopic': topics[1], 'useBinary': False}}])
        await nats_client.request(lib_name, req2.encode(), timeout=1)

    loop.run_until_complete(t())         
               
    try:                          
        startup_check(loop, lambda: verify_client_case(ping_req, None, topics[0], None, topics[1], None))
    except Exception:
        raise                                         

    try:
        async def warmup():
            request = [{}, {'fn._ping': {}}]
            await verify_client_case(request, None, topics[0], None, topics[1], None)

        loop.run_until_complete(warmup())
    except Exception:
        raise                                         
    
    yield topics

    async def t2():
        nats_client = await get_nats_client()
        req = json.dumps([{}, {'Stop': {'id': server_id}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)
        req2 = json.dumps([{}, {'Stop': {'id': cserver_id}}])
        await nats_client.request(lib_name, req2.encode(), timeout=1)

    loop.run_until_complete(t2()) 

    print('load_json_server_proc stopped')


def test_load_json_case(loop, load_json_server_proc):
    topics = load_json_server_proc

    async def t():
        for _ in range(10):
            req = [{}, {'fn.getData': {}}]
            await verify_client_case(req, None, topics[0], None, topics[1], None)
                                                 
    loop.run_until_complete(t())