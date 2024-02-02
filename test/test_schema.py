from test.util import verify_flat_case, ping_req, startup_check, Constants as c
import pytest
import json
from copy import deepcopy as dc


@pytest.fixture(scope="module")
def schema_server_proc(loop, nats_client, dispatcher_server):
    lib_name = dispatcher_server

    init_topics = ['frontdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'schema', t) for t in init_topics)     

    server_id = '{}.{}'.format(lib_name, 'schema')

    async def t():
        req = json.dumps([{}, {'StartSchemaServer': {'id': server_id, 'apiSchemaPath': c.schema_api_path, 'frontdoorTopic': topics[0]}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t())       

    try:
        startup_check(loop, lambda: verify_flat_case(nats_client, ping_req, None, *topics))
    except Exception:
        raise      

    yield topics

    async def t2():
        req = json.dumps([{}, {'Stop': {'id': server_id}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t2())        
    
    print('schema_server_proc stopped')

def test_schema_case(loop, schema_server_proc, nats_client, name, req, res):
    topics = schema_server_proc

    async def t():
        await verify_flat_case(nats_client, dc(req), dc(res), *topics)
                                             
    loop.run_until_complete(t())
