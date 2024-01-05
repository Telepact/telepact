from test.util import verify_server_case, verify_flat_case, verify_client_case, get_nats_client, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c, get_lib_modules
import asyncio
import pytest
import time
import importlib


@pytest.fixture(scope="module", params=get_lib_modules())
def rot_bin_client_server_proc(loop, nats_server, request):
    test_module_name = 'lib.{}.test_server'.format(request.param)
    print(test_module_name)
    l = importlib.import_module(test_module_name)


    ss = l.start_client_server(c.example_api_path, c.nats_url, 'cfront-rot-bin-client', 'cback-rot-bin-client', 'front-rot-bin-client', 'back-rot-bin-client')

    try:
        startup_check(loop, lambda: verify_client_case(ping_req, None,  'cfront-rot-bin-client', 'cback-rot-bin-client', 'front-rot-bin-client', 'back-rot-bin-client'))
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
    print('rot_bin_client_server_proc stopped')
    
def test_rotate_binary_client_case(loop, rot_bin_client_server_proc, name, statements):
    async def t():
        for request, expected_response in statements:
            await verify_client_case(request, expected_response, 'cfront-rot-bin-client', 'cback-rot-bin-client', 'front-rot-bin-client', 'back-rot-bin-client', use_binary=True)

    loop.run_until_complete(t())
