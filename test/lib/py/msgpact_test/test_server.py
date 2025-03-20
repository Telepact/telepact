from prometheus_client import CONTENT_TYPE_LATEST, Summary, CollectorRegistry, generate_latest, write_to_textfile
from nats.aio.client import Client as NatsClient
from nats.aio.msg import Msg
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
from nats.aio.client import Client as NATSClient, Subscription
import asyncio
import nats
from msgpact import SerializationError, Message, Serializer, Client, Server, MsgPactSchema, MockMsgPactSchema, MockServer, MsgPactSchemaFiles, MsgPactSchemaParseError
import traceback
import sys
from concurrent.futures import ThreadPoolExecutor
from msgpact_test.code_gen_handler import CodeGenHandler
from msgpact_test.gen.all_ import ClientInterface_, test as fntest


def on_err(e):
    print("".join(traceback.format_exception(e.__class__, e, e.__traceback__)))


def on_request_err(m):
    if m.headers.get("_onRequestError", False):
        raise RuntimeError()


def on_response_err(m):
    if m.headers.get("_onResponseError", False):
        raise RuntimeError()


async def start_client_test_server(connection: NatsClient, metrics: CollectorRegistry,
                                   client_frontdoor_topic: str,
                                   client_backdoor_topic: str,
                                   default_binary: bool,
                                   use_codegen: bool) -> Subscription:

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

    generated_client = ClientInterface_(client)

    async def message_handler(msg: Msg) -> None:
        request_bytes = msg.data

        print(f"   ->C  {request_bytes}")
        await connection.flush()

        request_pseudo_json = json.loads(request_bytes)
        request_headers, request_body = request_pseudo_json

        function_name, argument = next(iter(request_body.items()))

        @timers.time()
        async def c() -> 'Message':
            if use_codegen and function_name == "fn.test":
                headers, output = await generated_client.test(request_headers, fntest.Input(request_body))
                headers['_codegenc'] = True
                return Message(headers, output.pseudo_json)
            else:
                return await client.request(Message(request_headers, request_body))

        response = await c()

        response_pseudo_json = [response.headers, response.body]

        response_bytes = json.dumps(response_pseudo_json).encode()

        print(f"   <-C  {response_bytes}")
        await connection.publish(msg.reply, response_bytes)

    return await connection.subscribe(client_frontdoor_topic, cb=message_handler)


async def start_mock_test_server(connection: NatsClient, metrics: Any, api_schema_path: str,
                                 frontdoor_topic: str, config: Dict[str, Any]) -> Subscription:
    u_api = MockMsgPactSchema.from_directory(api_schema_path)

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
    server = MockServer(u_api, options)

    async def message_handler(msg: Msg) -> None:
        nonlocal server
        nonlocal connection

        request_bytes = msg.data

        print(f"    ->S {request_bytes}")
        await connection.flush()

        @timers.time()
        async def s():
            return await server.process(request_bytes)

        response_bytes = await s()

        print(f"    <-S {response_bytes}")
        await connection.publish(msg.reply, response_bytes)

    return await connection.subscribe(frontdoor_topic, cb=message_handler)


async def start_schema_test_server(connection: NatsClient, metrics: CollectorRegistry, api_schema_path: str, frontdoor_topic: str) -> Subscription:
    u_api = MsgPactSchema.from_directory(api_schema_path)

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
                    MsgPactSchema.from_file_json_map(
                        {'default': schema_json, 'extend': extend_json})
                else:
                    MsgPactSchema.from_json(schema_json)
            elif input_tag == 'Json':
                union_value = input[input_tag]
                schema_json = union_value.get("schema")
                MsgPactSchema.from_json(schema_json)
            elif input_tag == 'Directory':
                union_value = input[input_tag]
                schema_path = union_value.get("schemaDirectory")
                MsgPactSchema.from_directory(schema_path)
            else:
                raise RuntimeError("no matching schema input")
        except MsgPactSchemaParseError as e:
            on_err(e)
            return Message({}, {"ErrorValidationFailure": {"cases": e.schema_parse_failures_pseudo_json}})

        return Message({}, {"Ok_": {}})

    options = Server.Options()
    options.on_error = on_err
    options.auth_required = False
    server = Server(u_api, handler, options)

    async def handle_message(msg: Msg) -> None:
        nonlocal server
        nonlocal connection
        request_bytes = msg.data

        print(f"    ->S {request_bytes}")

        @timers.time()
        async def s():
            return await server.process(request_bytes)

        response_bytes = await s()

        print(f"    <-S {response_bytes}")
        await connection.publish(msg.reply, response_bytes)

    dispatcher = await connection.subscribe(frontdoor_topic, cb=handle_message)

    return dispatcher


async def start_test_server(connection: NatsClient, metrics: CollectorRegistry, api_schema_path: str, frontdoor_topic: str, backdoor_topic: str, auth_required: bool, use_codegen: bool) -> Subscription:
    files = MsgPactSchemaFiles(api_schema_path)
    alternate_map = files.filenames_to_json.copy()
    alternate_map["backwardsCompatibleChange"] = """
            [
                {
                    "struct.BackwardsCompatibleChange": {}
                }
            ]
            """

    u_api = MsgPactSchema.from_file_json_map(files.filenames_to_json)
    alternate_u_api = MsgPactSchema.from_file_json_map(alternate_map)

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
        request_bytes = json.dumps(request_pseudo_json).encode('utf-8')

        if use_codegen:
            print(f"     :H {request_bytes}")
            message = await code_gen_handler.handler(request_message)
            message.headers['_codegens'] = True
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
            "_toggleAlternateServer")
        if toggle_alternate_server == True:
            serve_alternate_server = not serve_alternate_server

        throw_error = request_headers.get("_throwError")
        if throw_error == True:
            raise ThisError()

        return message

    options = Server.Options()

    options.on_error = on_err
    options.on_request = on_request_err
    options.on_response = on_response_err
    options.auth_required = auth_required

    server = Server(u_api, handler, options)
    alternate_options = Server.Options()
    alternate_options.on_error = on_err
    alternate_options.auth_required = auth_required
    alternate_server = Server(
        alternate_u_api, handler, alternate_options)

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
                return await alternate_server.process(request_bytes)
            else:
                return await server.process(request_bytes)

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

    connection: NatsClient = await nats.connect(nats_url)

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
                server = await start_client_test_server(
                    connection, metrics, client_frontdoor_topic, client_backdoor_topic, use_binary, use_codegen)
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
