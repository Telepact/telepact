from test.util import verify_server_case, verify_flat_case, verify_client_case, get_nats_client, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c, get_lib_modules
import asyncio
import pytest
import time
import importlib


@pytest.fixture(scope="module", params=get_lib_modules())
def mock_server_proc(loop, nats_server, request):
    test_module_name = 'lib.{}.test_server'.format(request.param)
    print(test_module_name)
    l = importlib.import_module(test_module_name)

    s = l.start_mock_server(c.example_api_path, c.nats_url, 'front-mock')

    try:
        startup_check(loop, lambda: verify_flat_case(ping_req, None, 'front-mock'))
    except Exception:
        s.terminate()
        s.wait()
        raise      

    yield s
    s.terminate()
    s.wait()
    print('mock_server_proc stopped')

def test_mock_case(loop, mock_server_proc, name, statements):
    async def t():
        for request, expected_response in statements:
            await verify_flat_case(request, expected_response, 'front-mock')

    loop.run_until_complete(t())


def test_mock_invalid_case(loop, mock_server_proc, name, req, res):
    async def t():
        await verify_flat_case(req, res, 'front-mock')
    
    loop.run_until_complete(t())