from test.util import verify_server_case, verify_flat_case, verify_client_case, get_nats_client, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c, get_lib_modules
import asyncio
import pytest
import time
import importlib


@pytest.fixture(scope="module", params=get_lib_modules())
def binary_server_proc(loop, nats_server, request):
    test_module_name = 'lib.{}.test_server'.format(request.param)
    print(test_module_name)
    l = importlib.import_module(test_module_name)

    s = l.start_basic_server(c.binary_api_path, c.nats_url, 'front-binary', 'back-binary')

    try:
        startup_check(loop, lambda: verify_server_case(ping_req, None, 'front-binary', 'back-binary'))
    except Exception:
        s.terminate()
        s.wait()
        raise    

    yield s
    s.terminate()
    s.wait()
    print('binary_server_proc stopped')

def test_binary_case(loop, binary_server_proc, name, req, res):
    async def t():
        await verify_server_case(req, res, 'front-binary', 'back-binary')
    
    loop.run_until_complete(t())