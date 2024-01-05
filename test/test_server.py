from test.util import verify_server_case, verify_flat_case, verify_client_case, get_nats_client, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c, get_lib_modules
import asyncio
import pytest
import time
import os
import importlib


@pytest.fixture(scope="module", params=get_lib_modules())
def server_proc(loop, nats_server, request):
    lib_name = request.param
    test_module_name = 'lib.{}.test_server'.format(lib_name)
    l = importlib.import_module(test_module_name)

    init_topics = ['frontdoor', 'backdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'server', t) for t in init_topics)     
    
    s = l.start_basic_server(c.example_api_path, c.nats_url, *topics)
    
    try:                                
        startup_check(loop, lambda: verify_server_case(ping_req, None, *topics))
    except Exception:
        s.terminate()
        s.wait()
        raise   
    
    yield s, topics
    
    s.terminate()
    s.wait()
    print('basic_server_proc stopped')

def test_server_case(loop, server_proc, name, req, res):
    _, topics = server_proc
    
    async def t():
        await verify_server_case(req, res, *topics)
    
    loop.run_until_complete(t())