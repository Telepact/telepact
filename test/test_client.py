from test.util import verify_server_case, verify_flat_case, verify_client_case, get_nats_client, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c, get_lib_modules
import asyncio
import pytest
import time
import importlib

@pytest.fixture(scope="module", params=get_lib_modules())
def client_server_proc(loop, nats_server, request):
    test_module_name = request.param
    print(test_module_name)
    l = importlib.import_module(test_module_name)

    ss = l.start_client_server(c.example_api_path, c.nats_url, 'cfront-client', 'cback-client', 'front-client', 'back-client')

    try:
        startup_check(loop, lambda: verify_client_case(ping_req, None, 'cfront-client', 'cback-client', 'front-client', 'back-client'))
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
    print('client_server_proc stopped')

def test_client_case(loop, client_server_proc, name, req, expected_response):
    async def t():
        await verify_client_case(req, expected_response, 'cfront-client', 'cback-client', 'front-client', 'back-client')
                                             
    loop.run_until_complete(t())