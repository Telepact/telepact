from test.util import verify_server_case, verify_flat_case, verify_client_case, get_nats_client, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c, get_lib_modules
import asyncio
import pytest
import time
import importlib
import json


@pytest.fixture(scope="module", params=get_lib_modules())
def mock_server_proc(loop, nats_server, dispatcher_server, request):
    lib_name = request.param

    init_topics = ['frontdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'mock', t) for t in init_topics)     

    server_id = '{}.{}'.format(lib_name, 'mock')

    async def t():
        nats_client = await get_nats_client()
        req = json.dumps([{}, {'StartMockServer': {'id': server_id, 'apiSchemaPath': c.example_api_path, 'frontdoorTopic': topics[0]}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)    

    loop.run_until_complete(t())    

    try:
        startup_check(loop, lambda: verify_flat_case(ping_req, None, *topics))
    except Exception:
        raise      

    yield topics

    async def t2():
        nats_client = await get_nats_client()
        req = json.dumps([{}, {'Stop': {'id': server_id}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)    
    
    loop.run_until_complete(t2())         
    
    print('mock_server_proc stopped')

def test_mock_multi_case(loop, mock_server_proc, name, statements):
    topics = mock_server_proc

    async def t():
        for request, expected_response in statements:
            await verify_flat_case(request, expected_response, *topics)

    loop.run_until_complete(t())


def test_mock_case(loop, mock_server_proc, name, req, res):
    topics = mock_server_proc

    async def t():
        await verify_flat_case(req, res, *topics)
    
    loop.run_until_complete(t())