import json
from typing import Any
import msgpack
import nats
import asyncio
import subprocess
import pytest
import nats.aio.client
import time
import os
import copy
from nats.aio.msg import Msg

should_abort = False

class Constants:
    example_api_path = '../../test/example.uapi.json'
    binary_api_path = '../../test/binary.uapi.json'
    schema_api_path = '../../test/schema.uapi.json'
    load_api_path = '../../test/load.uapi.json'
    calculator_api_path = '../../test/calculator.uapi.json'
    nats_url = 'nats://127.0.0.1:4222'
    frontdoor_topic = 'frontdoor'
    intermediate_topic = 'intermediate'
    backdoor_topic = 'backdoor'

def increment():
    count = 0
    while True:
        yield count
        count += 1

def handler(request):
    header = request[0]
    body = request[1]
    target = next(iter(body))
    payload = body[target]

    response_header = {}

    if '_onResponseError' in header:
        response_header['_onResponseError'] = header['_onResponseError']

    if 'Ok' in header:
        return [response_header, {'Ok': header['Ok']}]
    elif 'result' in header:
        return [response_header, header['result']]
    elif 'throw' in header:
        return None
    else:
        return [response_header, {'Ok': {}}]


async def backdoor_handler(nats_client: nats.aio.client.Client, backdoor_topic):
    done = asyncio.get_running_loop().create_future()
    try:
        async def nats_handler(msg: Msg):
            backdoor_request_bytes = msg.data
            backdoor_request_json = backdoor_request_bytes.decode()
            backdoor_request = json.loads(backdoor_request_json)

            print(' B<-    {}'.format(backdoor_request), flush=True)

            backdoor_response = handler(backdoor_request)

            print(' B->    {}'.format(backdoor_response), flush=True)

            backdoor_response_json = json.dumps(backdoor_response)
            backdoor_response_bytes = backdoor_response_json.encode()        
            await nats_client.publish(msg.reply, backdoor_response_bytes)

            done.set_result(True)

        sub = await nats_client.subscribe(backdoor_topic, cb=nats_handler)

        await sub.unsubscribe(limit=1)
        await done
    except asyncio.exceptions.CancelledError:
        if sub:
            await sub.unsubscribe()        


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



async def client_backdoor_handler(nats_client, client_backdoor_topic, frontdoor_topic, times=1):
    try:
        request_was_binary = False
        request_binary_had_enough_integer_keys = False
        response_was_binary = False
        response_binary_had_enough_integer_keys = False

        received = 0
        done = asyncio.get_running_loop().create_future()

        async def nats_handler(msg):
            nonlocal request_was_binary
            nonlocal request_binary_had_enough_integer_keys
            nonlocal response_was_binary
            nonlocal response_binary_had_enough_integer_keys
            nonlocal received
            nonlocal done

            client_backdoor_request_bytes = msg.data
            try:
                client_backdoor_request_json = client_backdoor_request_bytes.decode()
                client_backdoor_request = json.loads(client_backdoor_request_json)
            except Exception:
                client_backdoor_request = msgpack.loads(client_backdoor_request_bytes, strict_map_key=False)
                request_was_binary = True
                try:
                    (int_keys, str_keys) = count_int_keys(client_backdoor_request[1])
                    request_binary_had_enough_integer_keys = int_keys >= str_keys
                except Exception as e:
                    print(e)
                    request_binary_had_enough_integer_keys = False

            print('  I<-   {}'.format(client_backdoor_request), flush=True)
            print('  i->   {}'.format(client_backdoor_request), flush=True)

            nats_response = await nats_client.request(frontdoor_topic, client_backdoor_request_bytes, timeout=10)

            frontdoor_response_bytes = nats_response.data

            print('  i<-   {}'.format(frontdoor_response_bytes), flush=True)

            try:
                frontdoor_response_json = frontdoor_response_bytes.decode()
                frontdoor_response = json.loads(frontdoor_response_json)
            except Exception:
                try:
                    frontdoor_response = msgpack.loads(frontdoor_response_bytes, strict_map_key=False)
                except Exception as e:
                    print(e)
                    raise

                response_was_binary = True
                try:
                    (int_keys, str_keys) = count_int_keys(frontdoor_response[1])
                    response_binary_had_enough_integer_keys = int_keys >= str_keys
                except Exception as e:
                    print(e)
                    response_binary_had_enough_integer_keys = False

            print('  i<-   {}'.format(frontdoor_response), flush=True)
            print('  I->   {}'.format(frontdoor_response), flush=True)

            await nats_client.publish(msg.reply, frontdoor_response_bytes)

            received += 1

            if (received >= times):
                done.set_result(True)


        sub = await nats_client.subscribe(client_backdoor_topic, cb=nats_handler)

        # TODO: This does not block until the subscription ends. Need to find another way to get the binary assertion results
        await sub.unsubscribe(limit=times)
        await done

        return request_was_binary, response_was_binary, request_binary_had_enough_integer_keys, response_binary_had_enough_integer_keys
    except asyncio.exceptions.CancelledError:
        if sub:
            await sub.unsubscribe()

def signal_handler(signum, frame):
    raise Exception("Timeout")


class hashabledict(dict):
  def __key(self):
    return tuple(sorted(self.items()))
  def __hash__(self):
    return hash(self.__key())
  def __eq__(self, other):
    return self.__key() == other.__key()
  

def convert_lists_to_sets(a):
    if type(a) == dict:
        for k,v in a.items():
            a[k] = convert_lists_to_sets(v)
        return hashabledict(a)
    elif type(a) == list:
        if type(next(iter(a))) == dict:
            return frozenset(convert_lists_to_sets(v) for v in a)
        else:
            return tuple(convert_lists_to_sets(v) for v in a)
    else:
        return a


async def verify_server_case(nats_client, request, expected_response, frontdoor_topic, backdoor_topic, just_send=False):
    assert_rules = {} if not expected_response or type(expected_response) == bytes else expected_response[0].pop('_assert', {})

    backdoor_handling_task = asyncio.create_task(backdoor_handler(nats_client, backdoor_topic))

    try:
        response = await send_case(nats_client, request, expected_response, frontdoor_topic, just_send=just_send)
    finally:
        backdoor_handling_task.cancel()
        await backdoor_handling_task

    if expected_response:
        if assert_rules.get('setCompare', False):
            expected_response = convert_lists_to_sets(expected_response)
            response = convert_lists_to_sets(response)
            
        assert expected_response == response


async def verify_flat_case(nats_client, request, expected_response, frontdoor_topic):
    assert_rules = {} if not expected_response else expected_response[0].pop('_assert', {})

    response = await send_case(nats_client, request, expected_response, frontdoor_topic)

    if expected_response:
        assert expected_response == response


async def verify_client_case(nats_client, request, expected_response, client_frontdoor_topic, client_backdoor_topic, frontdoor_topic, backdoor_topic, assert_binary=False):
    assert_rules = {} if not expected_response else expected_response[0].pop('_assert', {})

    client_times = 1
    if assert_rules.get('expectTwoRequests', False):
        client_times = 2

    client_handling_task = None if not client_backdoor_topic else asyncio.create_task(client_backdoor_handler(nats_client, client_backdoor_topic, frontdoor_topic, times=client_times))

    backdoor_handling_task = None if not backdoor_topic else asyncio.create_task(backdoor_handler(nats_client, backdoor_topic))

    try:
        response = await send_case(nats_client, request, expected_response, client_frontdoor_topic)
    finally:
        if backdoor_handling_task:
            backdoor_handling_task.cancel()
            await backdoor_handling_task
        if client_handling_task:
            client_handling_task.cancel()
            await client_handling_task
            (request_was_binary, response_was_binary, request_binary_had_enough_integer_keys, response_binary_had_enough_integer_keys) = client_handling_task.result() or (False, False, False, False)

    if assert_binary:
        if 'Error' not in next(iter(response[1])):
            assert '_bin' in response[0]

    response[0].pop('_bin', None)
    response[0].pop('_enc', None)
    response[0].pop('_pac', None)

    if expected_response:
        if assert_rules.get('setCompare', False):
            expected_response = convert_lists_to_sets(expected_response)
            response = convert_lists_to_sets(response)

        assert expected_response == response

    if assert_binary:
        if not assert_rules.get('skipBinaryCheck', False):
            assert request_was_binary == True
            assert response_was_binary == True

        if not assert_rules.get('skipFieldIdCheck', False):
            assert request_binary_had_enough_integer_keys == True
            assert response_binary_had_enough_integer_keys == True



async def send_case(nats_client: nats.aio.client.Client, request, expected_response, request_topic, just_send=False):

    print('T->     {}'.format(request), flush=True)

    request_is_msgpack = False
    if not just_send:
        request_is_msgpack = request[0].get('msgpack', False)

    if request_is_msgpack:
        request_bytes = msgpack.dumps(request)
    else:
        if not isinstance(request, bytes):
            request_json = json.dumps(request)
            request_bytes = request_json.encode()    
        else:
            request_bytes = request

    nats_response = await nats_client.request(request_topic, request_bytes, timeout=1)

    response_bytes = nats_response.data
    print('T<-     {}'.format(response_bytes), flush=True)

    try:
        response_json = response_bytes.decode()
        response = json.loads(response_json)
        print('T<-     {}'.format(response), flush=True)
    except:
        response = msgpack.loads(response_bytes, strict_map_key=False)
        print('T<-     {}'.format(response), flush=True)

    if 'numberTooBig' in response[0]:
        pytest.skip('Cannot use big numbers with msgpack')

    warnings = response[0].pop('_warnings', [])
    if warnings:
        warning_reasons = [next(iter(e['reason'])) for e in warnings]
        if 'NumberTruncated' in warning_reasons:
            pytest.skip('Target cannot handle large integers')

    if type(expected_response) == bytes:
        response = response_bytes

    return response

ping_req = [{},{'fn._ping': {}}]


async def ping(nats_client, topic):
    req = json.dumps([{}, {'Ping': {}}])
    await nats_client.request(topic, req.encode(), timeout=1)


def startup_check(loop: asyncio.AbstractEventLoop, verify, times=10):
    async def check():
        ex: Exception = None
        for _ in range(times):
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


