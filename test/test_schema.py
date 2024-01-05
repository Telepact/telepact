from test.util import verify_server_case, verify_flat_case, verify_client_case, get_nats_client, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c, get_lib_modules
import asyncio
import pytest
import time
import importlib


@pytest.fixture(scope="module", params=get_lib_modules())
def schema_server_proc(loop, nats_server, request):
    test_module_name = request.param
    print(test_module_name)
    l = importlib.import_module(test_module_name)

    s = l.start_schema_server(c.schema_api_path, c.nats_url, 'front-schema')

    try:
        startup_check(loop, lambda: verify_flat_case(ping_req, None, 'front-schema'))
    except Exception:
        s.terminate()
        s.wait()
        raise      

    yield s
    s.terminate()
    s.wait()
    print('schema_server_proc stopped')

def test_schema_case(loop, schema_server_proc, name, req, expected_response):
    async def t():
        await verify_flat_case(req, expected_response, 'front-schema')
                                             
    loop.run_until_complete(t())
