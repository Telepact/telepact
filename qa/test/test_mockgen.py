from util import verify_flat_case, ping_req, startup_check, Constants as c
import pytest
import json
from copy import deepcopy as dc


@pytest.fixture(scope="module")
def mockgen_server_proc(loop, nats_client, dispatcher_server):
    lib_name = dispatcher_server

    init_topics = ['frontdoor']
    topics = tuple('{}.{}.{}'.format(lib_name, 'mockgen', t)
                   for t in init_topics)

    server_id = '{}.{}'.format(lib_name, 'mockgen')

    async def t():
        req = json.dumps([{}, {'StartMockServer': {
                         'id': server_id, 'apiSchemaPath': c.mockgen_api_path, 'frontdoorTopic': topics[0]}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t())

    try:
        startup_check(loop, lambda: verify_flat_case(
            nats_client, ping_req, None, *topics))
    except Exception:
        raise

    yield topics

    async def t2():
        req = json.dumps([{}, {'Stop': {'id': server_id}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t2())

    print('mockgen_server_proc stopped')


def test_mockgen_multi_case(loop, mockgen_server_proc, nats_client, name, statements):
    topics = mockgen_server_proc

    async def t():
        for request, expected_response in statements:
            await verify_flat_case(nats_client, dc(request), dc(expected_response), *topics)

    loop.run_until_complete(t())
