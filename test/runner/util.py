#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

import json
from typing import Any
import msgpack
import asyncio
import subprocess
import pytest
import time
import os
import copy

should_abort = False


class Constants:
    example_api_path = '../../runner/schema/example'
    binary_api_path = '../../runner/schema/binary'
    schema_api_path = '../../runner/schema/parse'
    load_api_path = '../../runner/schema/load'
    auth_api_path = '../../runner/schema/auth'
    mockgen_api_path = '../../runner/schema/mockgen'
    calculator_api_path = '../../runner/schema/calculator'
    transport_url = 'stdio://local'
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

    response_header = header.get('@responseHeader', {})

    if '@onResponseError_' in header:
        response_header['@onResponseError_'] = header['@onResponseError_']

    if '@ok_' in header:
        return [response_header, {'Ok_': header['@ok_']}]
    elif '@result' in header:
        return [response_header, header['@result']]
    elif '@throw' in header:
        return None
    elif '@error' in header:
        return [response_header, {'ErrorExample2': {'field1': 'Boom!'}}]
    elif header.get('@override', None) != 'new':
        return [response_header, {'ErrorUnknown_': {}}]
    else:
        return [response_header, {'Ok_': {}}]


async def backdoor_handler(transport_client, backdoor_topic):
    done = asyncio.get_running_loop().create_future()
    try:
        async def transport_handler(msg):
            backdoor_request_bytes = msg.payload
            backdoor_request_json = backdoor_request_bytes.decode()
            backdoor_request = json.loads(backdoor_request_json)

            print(' B<-    {}'.format(backdoor_request), flush=True)

            backdoor_response = handler(backdoor_request)

            print(' B->    {}'.format(backdoor_response), flush=True)

            backdoor_response_json = json.dumps(backdoor_response)
            backdoor_response_bytes = backdoor_response_json.encode()
            await transport_client.send(msg.reply_channel, backdoor_response_bytes)

            done.set_result(True)

        sub = await transport_client.listen(backdoor_topic, cb=transport_handler)

        await sub.close(limit=1)
        await done
    except asyncio.exceptions.CancelledError:
        if sub:
            await sub.close()


def count_int_keys(m: dict):
    int_keys = 0
    str_keys = 0
    for k, v in m.items():
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


async def client_backdoor_handler(transport_client, client_backdoor_topic, frontdoor_topic, times=1):
    try:
        request_was_binary = False
        request_binary_had_enough_integer_keys = False
        response_was_binary = False
        response_binary_had_enough_integer_keys = False

        received = 0
        done = asyncio.get_running_loop().create_future()

        async def transport_handler(msg):
            nonlocal request_was_binary
            nonlocal request_binary_had_enough_integer_keys
            nonlocal response_was_binary
            nonlocal response_binary_had_enough_integer_keys
            nonlocal received
            nonlocal done

            client_backdoor_request_bytes = msg.payload
            try:
                client_backdoor_request_json = client_backdoor_request_bytes.decode()
                client_backdoor_request = json.loads(
                    client_backdoor_request_json)
            except Exception:
                client_backdoor_request = msgpack.loads(
                    client_backdoor_request_bytes, strict_map_key=False)
                request_was_binary = True
                try:
                    (int_keys, str_keys) = count_int_keys(
                        client_backdoor_request[1])
                    request_binary_had_enough_integer_keys = int_keys >= str_keys
                except Exception as e:
                    print(e)
                    request_binary_had_enough_integer_keys = False

            print('  I<-   {}'.format(client_backdoor_request), flush=True)
            print('  i->   {}'.format(client_backdoor_request), flush=True)

            transport_response = await transport_client.call(frontdoor_topic, client_backdoor_request_bytes, timeout=10)

            frontdoor_response_bytes = transport_response.payload

            print('  i<-   {}'.format(frontdoor_response_bytes), flush=True)

            try:
                frontdoor_response_json = frontdoor_response_bytes.decode()
                frontdoor_response = json.loads(frontdoor_response_json)
            except Exception:
                try:
                    frontdoor_response = msgpack.loads(
                        frontdoor_response_bytes, strict_map_key=False)
                except Exception as e:
                    print(e)
                    raise

                response_was_binary = True
                try:
                    (int_keys, str_keys) = count_int_keys(
                        frontdoor_response[1])
                    response_binary_had_enough_integer_keys = int_keys >= str_keys
                except Exception as e:
                    print(e)
                    response_binary_had_enough_integer_keys = False

            print('  i<-   {}'.format(frontdoor_response), flush=True)
            print('  I->   {}'.format(frontdoor_response), flush=True)

            await transport_client.send(msg.reply_channel, frontdoor_response_bytes)

            received += 1

            if (received >= times):
                done.set_result(True)

        sub = await transport_client.listen(client_backdoor_topic, cb=transport_handler)

        # TODO: This does not block until the subscription ends. Need to find another way to get the binary assertion results
        await sub.close(limit=times)
        await done

        return request_was_binary, response_was_binary, request_binary_had_enough_integer_keys, response_binary_had_enough_integer_keys
    except asyncio.exceptions.CancelledError:
        if sub:
            await sub.close()


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
        for k, v in a.items():
            a[k] = convert_lists_to_sets(v)
        return hashabledict(a)
    elif type(a) == list:
        if type(next(iter(a))) == dict:
            return frozenset(convert_lists_to_sets(v) for v in a)
        else:
            return tuple(convert_lists_to_sets(v) for v in a)
    else:
        return a


async def verify_server_case(transport_client, request, expected_response, frontdoor_topic, backdoor_topic, just_send=False):
    assert_rules = {} if not expected_response or type(
        expected_response) == bytes else expected_response[0].pop('@assert_', {})

    backdoor_handling_task = asyncio.create_task(
        backdoor_handler(transport_client, backdoor_topic))

    try:
        response = await send_case(transport_client, request, expected_response, frontdoor_topic, just_send=just_send)
    finally:
        backdoor_handling_task.cancel()
        await backdoor_handling_task

    if expected_response:
        if assert_rules.get('setCompare', False):
            expected_response = convert_lists_to_sets(expected_response)
            response = convert_lists_to_sets(response)

        assert expected_response == response


async def verify_flat_case(transport_client, request, expected_response, frontdoor_topic):
    assert_rules = {} if not expected_response else expected_response[0].pop(
        '@assert_', {})

    response = await send_case(transport_client, request, expected_response, frontdoor_topic)

    if expected_response:
        if assert_rules.get('setCompare', False):
            expected_response = convert_lists_to_sets(expected_response)
            response = convert_lists_to_sets(response)

        assert expected_response == response


async def verify_client_case(transport_client, request, expected_response, client_frontdoor_topic, client_backdoor_topic, frontdoor_topic, backdoor_topic, assert_binary=False):
    assert_rules = {} if not expected_response else expected_response[0].pop(
        '@assert_', {})

    client_times = 1
    if assert_rules.get('expectTwoRequests', False):
        client_times = 2

    client_handling_task = None if not client_backdoor_topic else asyncio.create_task(
        client_backdoor_handler(transport_client, client_backdoor_topic, frontdoor_topic, times=client_times))

    backdoor_handling_task = None if not backdoor_topic else asyncio.create_task(
        backdoor_handler(transport_client, backdoor_topic))

    try:
        response = await send_case(transport_client, request, expected_response, client_frontdoor_topic)
    finally:
        if backdoor_handling_task:
            backdoor_handling_task.cancel()
            await backdoor_handling_task
        if client_handling_task:
            client_handling_task.cancel()
            await client_handling_task
            (request_was_binary, response_was_binary, request_binary_had_enough_integer_keys,
             response_binary_had_enough_integer_keys) = client_handling_task.result() or (False, False, False, False)

    if assert_binary:
        if 'Error' not in next(iter(response[1])):
            assert '@bin_' in response[0]

    binary_was_used = response[0].pop('@bin_', None) is not None
    response[0].pop('@enc_', None)
    response[0].pop('@pac_', None)
    base64_was_used = response[0].pop('@base64_', None) is not None
    client_returned_binary = response[0].pop('@clientReturnedBinary', False)

    response_was_success = 'Ok_' in response[1]

    if expected_response:
        if assert_rules.get('setCompare', False):
            expected_response = convert_lists_to_sets(expected_response)
            response = convert_lists_to_sets(response)

        assert expected_response == response

    if assert_binary:
        if not assert_rules.get('skipBinaryCheck', False):
            assert request_was_binary == True

            if response_was_success:
                assert response_was_binary == True
            else:
                assert response_was_binary == False

        if not assert_rules.get('skipFieldIdCheck', False):
            assert request_binary_had_enough_integer_keys == True

            if response_was_success:
                assert response_binary_had_enough_integer_keys == True
            else:
                assert response_binary_had_enough_integer_keys == False

    if not binary_was_used:
        assert base64_was_used == client_returned_binary


async def send_case(transport_client, request, expected_response, request_topic, just_send=False):

    print('T->     {}'.format(request), flush=True)

    request_is_msgpack = False
    if not just_send:
        request_is_msgpack = request[0].get('@msgpack', False)

    if request_is_msgpack:
        request_bytes = msgpack.dumps(request)
    else:
        if not isinstance(request, bytes):
            request_json = json.dumps(request)
            request_bytes = request_json.encode()
        else:
            request_bytes = request

    transport_response = await transport_client.call(request_topic, request_bytes, timeout=10)

    response_bytes = transport_response.payload
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

    warnings = response[0].pop('@warn_', [])
    if warnings:
        warning_reasons = [next(iter(e['reason'])) for e in warnings]
        if 'NumberTruncated' in warning_reasons:
            pytest.skip('Target cannot handle large integers')

    if type(expected_response) == bytes:
        response = response_bytes

    return response

ping_req = [{}, {'fn.ping_': {}}]


async def ping(transport_client, topic):
    req = json.dumps([{}, {'Ping': {}}])
    await transport_client.call(topic, req.encode(), timeout=1)


def startup_check(loop: asyncio.AbstractEventLoop, verify, times=20):
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
