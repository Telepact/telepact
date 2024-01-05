from test.util import verify_server_case, verify_flat_case, verify_client_case, get_nats_client, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c, get_lib_modules
import asyncio
import pytest
import time
import os
import importlib

@pytest.fixture(scope="module", params=get_lib_modules())
def binary_client_server_proc(loop, nats_server, request):
    lib_name = request.param
    test_module_name = 'lib.{}.test_server'.format(lib_name)
    l = importlib.import_module(test_module_name)

    init_topics = ['client-frontdoor', 'client-backdoor', 'frontdoor', 'backdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'binary-client-server', t) for t in init_topics)    

    ss = l.start_client_server(c.example_api_path, c.nats_url, *topics)
               
    try:                          
        startup_check(loop, lambda: verify_client_case(ping_req, None, *topics))
    except Exception:
        for s in ss:
            s.terminate()
        for s in ss:
            s.wait()
        raise                                         

    try:
        async def warmup():
            request = [{'_binary': True}, {'fn._ping': {}}]
            await verify_client_case(request, None, *topics)

        loop.run_until_complete(warmup())
    except Exception:
        for s in ss:
            s.terminate()
        for s in ss:
            s.wait()
        raise                                         
    
    yield ss, topics

    for s in ss:
        s.terminate()
    for s in ss:
        s.wait()                        
    
def test_binary_client_server_case(loop, binary_client_server_proc, name, req, res):
    _, topics = binary_client_server_proc

    async def t():
        await verify_client_case(req, res, *topics, use_binary=True)
                                                 
    loop.run_until_complete(t())