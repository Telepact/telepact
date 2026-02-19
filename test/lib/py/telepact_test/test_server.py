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

from prometheus_client import CONTENT_TYPE_LATEST, Summary, CollectorRegistry, generate_latest, write_to_textfile
from typing import List, Any
from threading import Lock, Condition
import csv
from typing import Any, Dict, List, Optional
import threading
import os
from datetime import timedelta
from time import time as timer
from typing import Callable, Any, Dict, List, Union
from typing import Dict
from pathlib import Path
from typing import Dict, Any, List, Callable, Union
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import json
import asyncio
from telepact import SerializationError, Message, Serializer, Client, Server, TelepactSchema, MockTelepactSchema, MockServer, TelepactSchemaFiles, TelepactSchemaParseError, TestClient
import traceback
import sys
from concurrent.futures import ThreadPoolExecutor
from telepact_test.code_gen_handler import CodeGenHandler
from telepact_test.gen.gen_types import TypedClient, test as fntest
from telepact_test.stdio_nats import Client as NatsClient, Subscription, Msg, connect as stdio_connect
import base64


def on_err(e):
    print("".join(traceback.format_exception(e.__class__, e, e.__traceback__)))


def on_request_err(m):
    if m.headers.get("@onRequestError_", False):
        raise RuntimeError()


def on_response_err(m):
    if m.headers.get("@onResponseError_", False):
        raise RuntimeError()
    

def find_bytes(obj):
  if isinstance(obj, bytes):
    return True

  if isinstance(obj, dict):
    for value in obj.values():
      if find_bytes(value):
        return True
  
  elif isinstance(obj, (list, tuple)):
    for item in obj:
      if find_bytes(item):
        return True

  return False


async def start_client_test_server(connection: NatsClient, metrics: CollectorRegistry,
                                   client_frontdoor_topic: str,
                                   client_backdoor_topic: str,
                                   default_binary: bool,
                                   use_codegen: bool,
                                   use_test_client: bool) -> Subscription:

    timers = Summary(client_frontdoor_topic.replace(
        '.', '_').replace('-', '_'), '', registry=metrics)

    async def adapter(m: Message, s: Serializer) -> Message:
        try:
            request_bytes = s.serialize(m)
        except SerializationError as e:
            if isinstance(e.__context__, OverflowError):
                return Message({"numberTooBig": True}, {"ErrorUnknown_": {}})
            else:
                raise

        print(f"   <-c  {request_bytes}")
        await connection.flush()

        try:
            nats_response_message = await connection.request(client_backdoor_topic, request_bytes, 5)
        except asyncio.TimeoutError:
            raise RuntimeError(
                "Timeout occurred while waiting for NATS response.")

        response_bytes = nats_response_message.data

        print(f"   ->c  {response_bytes}")
        await connection.flush()

        response_message = s.deserialize(response_bytes)
        return response_message

    options = Client.Options()
    options.use_binary = default_binary
    options.always_send_json = not default_binary
    client = Client(adapter, options)

    test_client_options = TestClient.Options()
    test_client = TestClient(client, test_client_options)

    generated_client = TypedClient(client)

    async def message_handler(msg: Msg) -> None:
        request_bytes = msg.data

        print(f"   ->C  {request_bytes}")
        await connection.flush()

        request_pseudo_json = json.loads(request_bytes)
        request_headers, request_body = request_pseudo_json

        function_name, argument = next(iter(request_body.items()))

        @timers.time()
        async def c() -> 'Message':
            if use_test_client:
                try:
                    reset_seed = request_headers.get("@setSeed")
                    if reset_seed is not None:
                        test_client.set_seed(reset_seed)
                    expected_pseudo_json_body = request_headers.get("@expectedPseudoJsonBody")
                    expect_match = request_headers.get("@expectMatch", True)
                    return await test_client.assert_request(Message(request_headers, request_body), expected_pseudo_json_body, expect_match)
                except Exception as e:
                    on_err(e)
                    response_headers = {}
                    if isinstance(e, AssertionError):
                        response_headers["@assertionError"] = True
                    return Message(response_headers, {"ErrorUnknown_": {}})
            elif use_codegen and function_name == "fn.test":
                headers, output = await generated_client.test(request_headers, fntest.Input(request_body))
                headers['@codegenc_'] = True
                return Message(headers, output.pseudo_json)
            else:
                return await client.request(Message(request_headers, request_body))

        response = await c()

        if find_bytes(response.body):
            response.headers['@clientReturnedBinary'] = True

        response_pseudo_json = [response.headers, response.body]

        def custom_converter(obj):
            if isinstance(obj, bytes):
                return base64.b64encode(obj).decode('utf-8')
            raise TypeError('Object of type {obj.__class__.__name__} is not JSON serializable')

        response_bytes = json.dumps(response_pseudo_json, default=custom_converter).encode()

        print(f"   <-C  {response_bytes}")
        await connection.publish(msg.reply, response_bytes)

    return await connection.subscribe(client_frontdoor_topic, cb=message_handler)


async def start_mock_test_server(connection: NatsClient, metrics: Any, api_schema_path: str,
                                 frontdoor_topic: str, config: Dict[str, Any]) -> Subscription:
    telepact = MockTelepactSchema.from_directory(api_schema_path)

    options = MockServer.Options()
    options.on_error = on_err
    options.enable_message_response_generation = False

    if config is not None:
        options.generated_collection_length_min = config.get("minLength")
        options.generated_collection_length_max = config.get("maxLength")
        options.enable_message_response_generation = config.get(
            "enableGen", False)

    timers = Summary(frontdoor_topic.replace(
        '.', '_').replace('-', '_'), '', registry=metrics)
    server = MockServer(telepact, options)

    async def message_handler(msg: Msg) -> None:
        nonlocal server
        nonlocal connection

        request_bytes = msg.data

        print(f"    ->S {request_bytes}")
        await connection.flush()

        @timers.time()
        async def s():
            response = await server.process(request_bytes)
            return response.bytes

        response_bytes = await s()

        print(f"    <-S {response_bytes}")
        await connection.publish(msg.reply, response_bytes)

    return await connection.subscribe(frontdoor_topic, cb=message_handler)


async def start_schema_test_server(connection: NatsClient, metrics: CollectorRegistry, api_schema_path: str, frontdoor_topic: str) -> Subscription:
    telepact = TelepactSchema.from_directory(api_schema_path)

    timers = Summary(frontdoor_topic.replace(
        '.', '_').replace('-', '_'), '', registry=metrics)

    async def handler(request_message: 'Message') -> 'Message':
        request_body = request_message.body

        arg = request_body.get("fn.validateSchema", {})
        input = arg.get("input")

        input_tag = next(iter(input.keys()))

        try:
            if input_tag == 'PseudoJson':
                union_value = input[input_tag]
                schema_json = union_value.get("schema")
                extend_json = union_value.get("extend!")

                if extend_json:
                    TelepactSchema.from_file_json_map(
                        {'default': schema_json, 'extend': extend_json})
                else:
                    TelepactSchema.from_json(schema_json)
            elif input_tag == 'Json':
                union_value = input[input_tag]
                schema_json = union_value.get("schema")
                TelepactSchema.from_json(schema_json)
            elif input_tag == 'Directory':
                union_value = input[input_tag]
                schema_path = union_value.get("schemaDirectory")
                TelepactSchema.from_directory(schema_path)
            else:
                raise RuntimeError("no matching schema input")
        except TelepactSchemaParseError as e:
            on_err(e)
            return Message({}, {"ErrorValidationFailure": {"cases": e.schema_parse_failures_pseudo_json}})

        return Message({}, {"Ok_": {}})

    options = Server.Options()
    options.on_error = on_err
    options.auth_required = False
    server = Server(telepact, handler, options)

    async def handle_message(msg: Msg) -> None:
        nonlocal server
        nonlocal connection
        request_bytes = msg.data

        print(f"    ->S {request_bytes}")

        @timers.time()
        async def s():
            response = await server.process(request_bytes)
            return response.bytes

        response_bytes = await s()

        print(f"    <-S {response_bytes}")
        await connection.publish(msg.reply, response_bytes)

    dispatcher = await connection.subscribe(frontdoor_topic, cb=handle_message)

    return dispatcher


async def start_test_server(connection: NatsClient, metrics: CollectorRegistry, api_schema_path: str, frontdoor_topic: str, backdoor_topic: str, auth_required: bool, use_codegen: bool) -> Subscription:
    files = TelepactSchemaFiles(api_schema_path)
    alternate_map = files.filenames_to_json.copy()
    alternate_map["backwardsCompatibleChange"] = """
            [
                {
                    "struct.BackwardsCompatibleChange": {}
                }
            ]
            """

    telepact = TelepactSchema.from_file_json_map(files.filenames_to_json)
    alternate_telepact = TelepactSchema.from_file_json_map(alternate_map)

    timers = Summary(frontdoor_topic.replace(
        '.', '_').replace('-', '_'), '', registry=metrics)

    serve_alternate_server = False

    code_gen_handler = CodeGenHandler()

    executor = ThreadPoolExecutor()

    class ThisError(RuntimeError):
        pass

    async def handler(request_message: 'Message') -> 'Message':
        nonlocal serve_alternate_server
        nonlocal executor

        request_headers = request_message.headers
        request_body = request_message.body
        request_pseudo_json = [request_headers, request_body]

        def default_serializer(obj):
            if isinstance(obj, bytes):
                return base64.b64encode(obj).decode('utf-8')
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        request_bytes = json.dumps(request_pseudo_json, default=default_serializer).encode('utf-8')

        if use_codegen:
            print(f"     :H {request_bytes}")
            message = await code_gen_handler.handler(request_message)
            message.headers['@codegens_'] = True
        else:
            print(f"    <-s {request_bytes}")

            nats_response_message: Msg = await connection.request(
                backdoor_topic, request_bytes, timeout=5)

            response_bytes = nats_response_message.data

            print(f"    ->s {response_bytes}")

            response_pseudo_json = json.loads(response_bytes.decode('utf-8'))

            response_headers = response_pseudo_json[0]
            response_body = response_pseudo_json[1]

            message = Message(response_headers, response_body)

        toggle_alternate_server = request_headers.get(
            "@toggleAlternateServer_")
        if toggle_alternate_server == True:
            serve_alternate_server = not serve_alternate_server

        throw_error = request_headers.get("@throwError_")
        if throw_error == True:
            raise ThisError()

        return message

    options = Server.Options()

    options.on_error = on_err
    options.on_request = on_request_err
    options.on_response = on_response_err
    options.auth_required = auth_required

    server = Server(telepact, handler, options)
    alternate_options = Server.Options()
    alternate_options.on_error = on_err
    alternate_options.auth_required = auth_required
    alternate_server = Server(
        alternate_telepact, handler, alternate_options)

    async def handle_test_message(msg: Msg) -> None:
        nonlocal serve_alternate_server
        nonlocal alternate_server
        nonlocal server
        nonlocal connection
        request_bytes = msg.data

        print(f"    ->S {request_bytes}")

        @timers.time()
        async def s():
            nonlocal serve_alternate_server
            nonlocal alternate_server
            nonlocal server

            if serve_alternate_server:
                response = await alternate_server.process(request_bytes)
                return response.bytes
            else:
                override_headers = {'@override': 'old'}
                response = await server.process(request_bytes, override_headers)
                return response.bytes

        response_bytes = await s()

        print(f"    <-S {response_bytes}")
        await connection.publish(msg.reply, response_bytes)

    dispatcher = await connection.subscribe(frontdoor_topic, cb=handle_test_message)

    print(f"Test server listening on {frontdoor_topic}")

    return dispatcher


async def run_dispatcher_server():
    print('Starting dispatcher')
    nats_url = os.getenv("NATS_URL")
    if nats_url is None:
        raise RuntimeError("NATS_URL env var not set")

    done = asyncio.get_running_loop().create_future()

    metrics = CollectorRegistry()
    metrics_file = "./metrics.txt"

    servers: dict[str, Subscription] = {}

    def publish_metrics():
        with open(metrics_file, "w") as f:
            f.write(generate_latest(metrics).decode("utf-8"))

    connection: NatsClient = await stdio_connect(nats_url)

    async def message_handler(msg):
        request_bytes = msg.data

        print(f"    ->S {request_bytes.decode('utf-8')}")
        response_bytes = b""

        try:
            request = json.loads(request_bytes)
            body = request[1]
            entry = next(iter(body.items()))
            target = entry[0]
            payload = entry[1]

            if target == "Ping":
                pass
            elif target == "End":
                done.set_result(True)
            elif target == "Stop":
                server_id = payload["id"]
                server = servers.get(server_id)
                if server:
                    await server.drain()
            elif target == "StartServer":
                server_id = payload["id"]
                api_schema_path = payload["apiSchemaPath"]
                frontdoor_topic = payload["frontdoorTopic"]
                backdoor_topic = payload["backdoorTopic"]
                auth_required = payload.get('authRequired', False)
                use_codegen = payload.get('useCodeGen', False)
                server = await start_test_server(
                    connection, metrics, api_schema_path, frontdoor_topic, backdoor_topic, auth_required, use_codegen)
                servers[server_id] = server
            elif target == "StartClientServer":
                server_id = payload["id"]
                client_frontdoor_topic = payload["clientFrontdoorTopic"]
                client_backdoor_topic = payload["clientBackdoorTopic"]
                use_binary = payload.get("useBinary", False)
                use_codegen = payload.get('useCodeGen', False)
                use_test_client = payload.get('useTestClient', False)
                server = await start_client_test_server(
                    connection, metrics, client_frontdoor_topic, client_backdoor_topic, use_binary, use_codegen, use_test_client)
                servers[server_id] = server
            elif target == "StartMockServer":
                server_id = payload["id"]
                api_schema_path = payload["apiSchemaPath"]
                frontdoor_topic = payload["frontdoorTopic"]
                config = payload.get('config!', None)
                server = await start_mock_test_server(
                    connection, metrics, api_schema_path, frontdoor_topic, config)
                servers[server_id] = server
            elif target == "StartSchemaServer":
                server_id = payload["id"]
                api_schema_path = payload["apiSchemaPath"]
                frontdoor_topic = payload["frontdoorTopic"]
                server = await start_schema_test_server(
                    connection, metrics, api_schema_path, frontdoor_topic)
                servers[server_id] = server
            else:
                raise RuntimeError("no matching server")

            response_bytes = json.dumps([{}, {"Ok_": {}}]).encode("utf-8")

        except Exception as e:
            on_err(e)
            try:
                response_bytes = json.dumps(
                    [{}, {"ErrorUnknown": {}}]).encode("utf-8")
            except json.JSONDecodeError:
                raise

        print(f"    <-S {response_bytes.decode('utf-8')}")
        await connection.publish(msg.reply, response_bytes)

    dispatcher = await connection.subscribe("py", cb=message_handler)

    await done

    publish_metrics()

    print("Dispatcher exiting")
