from test.util import verify_server_case, verify_flat_case, verify_client_case, get_nats_client, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c, get_lib_modules
import asyncio
import pytest
import time
import os
import importlib
import json


@pytest.fixture(scope="module", params=get_lib_modules())
def server_proc(loop, nats_server, dispatcher_server, request):
    lib_name = request.param

    init_topics = ['frontdoor', 'backdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'server', t) for t in init_topics)

    server_id = '{}.{}'.format(lib_name, 'server')

    async def t():
        nats_client = await get_nats_client()
        req = json.dumps([{}, {'StartServer': {'id': server_id, 'apiSchemaPath': c.example_api_path, 'frontdoorTopic': topics[0], 'backdoorTopic': topics[1]}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t())    
    
    try:                                
        startup_check(loop, lambda: verify_server_case(ping_req, None, *topics))
    except Exception:
        raise   
    
    yield topics

    async def t2():
        nats_client = await get_nats_client()
        req = json.dumps([{}, {'Stop': {'id': server_id}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t2())    
    
    print('basic_server_proc stopped')

def test_server_case(loop, server_proc, name, req, res):
    topics = server_proc
    
    async def t():
        await verify_server_case(req, res, *topics)
    
    loop.run_until_complete(t())