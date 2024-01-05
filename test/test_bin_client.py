from test.util import verify_server_case, verify_flat_case, verify_client_case, get_nats_client, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c, get_lib_modules
import asyncio
import pytest
import time
import os
import importlib

@pytest.fixture(scope="module", params=get_lib_modules())
def bin_client_server_proc(loop, nats_server, request):
    test_module_name = request.param
    print(test_module_name)
    l = importlib.import_module(test_module_name)

    ss = l.start_client_server(c.example_api_path, c.nats_url, 'cfront-bin-client', 'cback-bin-client', 'front-bin-client', 'back-bin-client')
               
    try:                          
        startup_check(loop, lambda: verify_client_case(ping_req, None, 'cfront-bin-client', 'cback-bin-client', 'front-bin-client', 'back-bin-client'))
    except Exception:
        for s in ss:
            s.terminate()
        for s in ss:
            s.wait()
        raise                                         

    try:
        async def warmup():
            request = [{}, {'fn._ping': {}}]
            await verify_client_case(request, None, 'cfront-bin-client', 'cback-bin-client', 'front-bin-client', 'back-bin-client', use_binary=True)

        loop.run_until_complete(warmup())
    except Exception:
        for s in ss:
            s.terminate()
        for s in ss:
            s.wait()
        raise                                         
    
    yield ss
    for s in ss:
        s.terminate()
    for s in ss:
        s.wait()                        
    print('bin_client_server_proc stopped')
    
def test_binary_client_case(loop, bin_client_server_proc, name ,req, expected_response):
    async def t():
        await verify_client_case(req, expected_response, 'cfront-bin-client', 'cback-bin-client', 'front-bin-client', 'back-bin-client', use_binary=True)
                                                 
    loop.run_until_complete(t())