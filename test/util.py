import json
import msgpack
import nats
import asyncio
import subprocess
import pytest
import nats.aio.client
import time

should_abort = False

class Constants:
    example_api_path = '../../test/example.japi.json'
    binary_api_path = '../../test/binary.japi.json'
    schema_api_path = '../../test/schema.japi.json'
    nats_url = 'nats://127.0.0.1:4222'
    frontdoor_topic = 'frontdoor'
    intermediate_topic = 'intermediate'
    backdoor_topic = 'backdoor'

def handler(request):
    header = request[0]
    body = request[1]
    target = next(iter(body))
    payload = body[target]

    match target:
        case 'fn.test':
            if 'Ok' in header:
                return [{}, {'Ok': header['Ok']}]
            elif 'result' in header:
                return [{}, header['result']]
            elif 'throw' in header:
                return None
            else:
                return [{}, {}]


async def backdoor_handler(backdoor_topic):
    nats_client = await get_nats_client()

    async def nats_handler(msg):
        backdoor_request_bytes = msg.data
        backdoor_request_json = backdoor_request_bytes.decode()
        backdoor_request = json.loads(backdoor_request_json)

        print(' B<-    {}'.format(backdoor_request), flush=True)

        backdoor_response = handler(backdoor_request)

        print(' B->    {}'.format(backdoor_response), flush=True)

        backdoor_response_json = json.dumps(backdoor_response)
        backdoor_response_bytes = backdoor_response_json.encode()        
        await nats_client.publish(msg.reply, backdoor_response_bytes)

    sub = await nats_client.subscribe(backdoor_topic, cb=nats_handler)

    await sub.unsubscribe(limit=1)


def count_int_keys(m: dict):
    int_keys = 0
    str_keys = 0
    for k,v in m.items():
        if type(k) == int:
            int_keys += 1
        else:
            str_keys += 1
        if type(v) == dict:
            (this_int_keys, this_str_keys) = count_int_keys(v)
            int_keys += this_int_keys
            str_keys += this_str_keys
    return (int_keys, str_keys)


class NotEnoughIntegerKeys(Exception):
    pass



async def client_backdoor_handler(client_backdoor_topic, frontdoor_topic, times=1):
    nats_client = await get_nats_client()

    async def nats_handler(msg):
        client_backdoor_request_bytes = msg.data
        try:
            client_backdoor_request_json = client_backdoor_request_bytes.decode()
            client_backdoor_request = json.loads(client_backdoor_request_json)
        except Exception:
            client_backdoor_request = msgpack.loads(client_backdoor_request_bytes, strict_map_key=False)
            # TODO: Verify binary is done when it's supposed to be done

        print('  I<-   {}'.format(client_backdoor_request), flush=True)
        print('  i->   {}'.format(client_backdoor_request), flush=True)

        nats_response = await nats_client.request(frontdoor_topic, client_backdoor_request_bytes, timeout=10)

        frontdoor_response_bytes = nats_response.data

        try:
            frontdoor_response_json = frontdoor_response_bytes.decode()
            frontdoor_response = json.loads(frontdoor_response_json)
        except Exception:
            frontdoor_response = msgpack.loads(frontdoor_response_bytes, strict_map_key=False)
            # TODO: verify binary is done when it's supposed to be done

        print('  i<-   {}'.format(frontdoor_response), flush=True)
        print('  I->   {}'.format(frontdoor_response), flush=True)

        await nats_client.publish(msg.reply, frontdoor_response_bytes)

    sub = await nats_client.subscribe(client_backdoor_topic, cb=nats_handler)

    await sub.unsubscribe(limit=times)


def signal_handler(signum, frame):
    raise Exception("Timeout")


nc = None

async def get_nats_client():
    global nc
    if not nc:
        nc = await nats.connect(Constants.nats_url) 
    return nc


def start_nats_server():
    return subprocess.Popen(['nats-server', '-DV'])


async def verify_server_case(request, expected_response, frontdoor_topic, backdoor_topic):

    backdoor_handling_task = asyncio.create_task(backdoor_handler(backdoor_topic))

    try:
        response = await send_case(request, expected_response, frontdoor_topic)
    finally:
        backdoor_handling_task.cancel()
        await backdoor_handling_task

    if expected_response:
        assert expected_response == response


async def verify_flat_case(request, expected_response, frontdoor_topic):

    response = await send_case(request, expected_response, frontdoor_topic)

    if expected_response:
        assert expected_response == response


async def verify_client_case(request, expected_response, client_frontdoor_topic, client_backdoor_topic, frontdoor_topic, backdoor_topic, use_binary=False, enforce_binary=False, enforce_integer_keys=False, times=1):

    client_handling_task = asyncio.create_task(client_backdoor_handler(client_backdoor_topic, frontdoor_topic, times=times))    
    backdoor_handling_task = asyncio.create_task(backdoor_handler(backdoor_topic))

    if use_binary:
        request[0]['_binary'] = True

    try:
        response = await send_case(request, expected_response, client_frontdoor_topic)
    finally:
        backdoor_handling_task.cancel()
        client_handling_task.cancel()
        await backdoor_handling_task
        await client_handling_task

    if use_binary:
        if 'Error' not in next(iter(response[1])):
            assert '_bin' in response[0]
        response[0].pop('_bin', None)
        response[0].pop('_enc', None)

    if expected_response:
        assert expected_response == response

    # TODO: verify that binary was being done    


async def send_case(request, expected_response, request_topic):
    nats_client = await get_nats_client()

    print('T->     {}'.format(request), flush=True)

    if type(request) == bytes:
        request_bytes = request
    else:
        request_json = json.dumps(request)
        request_bytes = request_json.encode()    

    nats_response = await nats_client.request(request_topic, request_bytes, timeout=1)

    response_bytes = nats_response.data

    if type(expected_response) == bytes:
        response = response_bytes
    else:
        response_json = response_bytes.decode()
        response = json.loads(response_json)    

    print('T<-     {}'.format(response), flush=True)

    if 'numberTooBig' in response[0]:
        pytest.skip('Cannot use big numbers with msgpack')

    return response

ping_req = [{},{'fn._ping': {}}]

def startup_check(loop: asyncio.AbstractEventLoop, verify):
    async def check():
        ex: Exception = None
        for _ in range(10):
            try:
                await verify()
                print('Server successfully started.')
                return
            except Exception as e:
                ex = e
                print('Server not yet ready...')
                print(e)
                time.sleep(1)
        
        raise Exception('Server did not startup correctly') from ex
    
    loop.run_until_complete(check())


