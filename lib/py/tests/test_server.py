from prometheus_client.exposition import Histogram, push_to_gateway
from prometheus_client import MetricRegistry, generate_latest, CONTENT_TYPE_LATEST, Summary
from nats.aio.client import Client as NatsClient
from typing import List, Map, Any
from threading import Lock, Condition
import csv
from prometheus_client import CollectorRegistry, generate_latest, write_to_textfile
from nats.aio.options import Options
from nats import NATS, Msg
from typing import Any, Dict, List, Optional
import threading
import os
from datetime import timedelta
from threading import AtomicBoolean
from time import time as timer
from typing import Callable, Any, Dict, List, Union
from nats.aio.client import Client as NATSClient
from typing import Dict
from pathlib import Path
from typing import Dict, Any, List, Callable, Union
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import json
from nats.aio.client import Client as NATSClient, Msg, Subscription
from uapi.types import UApiSchema, MockServer, UApiSchemaParseError
import asyncio


async def start_client_test_server(connection: NATSClient, metrics: CollectorRegistry,
                                   client_frontdoor_topic: str,
                                   client_backdoor_topic: str,
                                   default_binary: bool) -> Subscription:

    timers = Summary(client_frontdoor_topic, registry=metrics)

    def adapter(m: Msg, s: Any) -> Union[Dict[str, bool], Dict[str, Dict[str, Any]]]:
        async def async_task() -> Union[Dict[str, bool], Dict[str, Dict[str, Any]]]:
            try:
                request_bytes = await s.serialize(m)

                print(f"   <-c  {request_bytes.decode()}")
                await connection.flush()

                try:
                    nats_response_message = await connection.request(client_backdoor_topic, request_bytes, 5)
                except asyncio.TimeoutError:
                    raise RuntimeError(
                        "Timeout occurred while waiting for NATS response.")

                response_bytes = nats_response_message.data

                print(f"   ->c  {response_bytes.decode()}")
                await connection.flush()

                response_message = await s.deserialize(response_bytes)
                return response_message
            except Exception as e:
                raise RuntimeError(e)

        return async_task

    options = {
        "use_binary": default_binary
    }
    client = NATSClient(adapter, **options)

    async def message_handler(msg: Msg) -> None:
        try:
            request_bytes = msg.data

            print(f"   ->C  {request_bytes.decode()}")
            await connection.flush()

            request_pseudo_json = json.loads(request_bytes)
            request_headers, request_body = request_pseudo_json

            @timers.time()
            async def c():
                return await client.request(request_headers, request_body)

            response = c()

            response_pseudo_json = [response.header, response.body]

            print(response_pseudo_json)

            response_bytes = json.dumps(response_pseudo_json).encode()

            print(f"   <-C  {response_bytes.decode()}")
            await connection.publish(msg.reply_to, response_bytes)
        except Exception as e:
            raise RuntimeError(e)

    return connection.subscribe(client_frontdoor_topic, cb=message_handler)


async def start_mock_test_server(connection: NATSClient, metrics: Any, api_schema_path: str,
                                 frontdoor_topic: str, config: Dict[str, Any]) -> Subscription:
    api_schema_content = Path(api_schema_path).read_text()
    u_api = UApiSchema.from_json(api_schema_content)

    options = {
        "on_error": lambda e: print(e),
        "enable_message_response_generation": False
    }

    if config is not None:
        options.update({
            "generated_collection_length_min": config.get("minLength"),
            "generated_collection_length_max": config.get("maxLength"),
            "enable_message_response_generation": config.get("enableGen", False)
        })

    timers = Summary(frontdoor_topic, registry=metrics)
    server = MockServer(u_api, **options)

    async def message_handler(msg: Msg) -> None:
        try:
            request_bytes = msg.data

            print(f"    ->S {request_bytes.decode()}")
            await connection.flush()

            @timers.time()
            def s():
                return server.process(request_bytes)

            response_bytes = s()

            print(f"    <-S {response_bytes.decode()}")
            await connection.publish(msg.reply_to, response_bytes)
        except Exception as e:
            raise RuntimeError(e)

    return connection.subscribe(frontdoor_topic, cb=message_handler)


class Message:
    def __init__(self, header: Dict[str, Any], body: Dict[str, Any]):
        self.header = header
        self.body = body


class Server:
    class Options:
        def __init__(self):
            self.onError = None
            self.onRequest = None
            self.onResponse = None

    def __init__(self, u_api, handler: Callable[[Message], Message], options: Options):
        self.u_api = u_api
        self.handler = handler
        self.options = options

    def process(self, request_bytes: bytes) -> bytes:
        return self.handler(request_bytes)


def start_schema_test_server(connection: Any, metrics: CollectorRegistry, api_schema_path: str, frontdoor_topic: str) -> Subscription:
    json_data = Path(api_schema_path).read_text()
    u_api = UApiSchema.from_json(json_data)

    timers = Summary(frontdoor_topic, registry=metrics)

    def handler(request_message: Message) -> Message:
        request_body = request_message.body

        arg = request_body.get("fn.validateSchema", {})
        schema_pseudo_json = arg.get("schema")
        extend_schema_json = arg.get("extend!")

        serialize_schema = request_message.header.get("_serializeSchema", True)

        if serialize_schema:
            try:
                schema_json_bytes = json.dumps(
                    schema_pseudo_json).encode('utf-8')
                schema_json = schema_json_bytes.decode('utf-8')
            except Exception as e:
                raise RuntimeError(e)
        else:
            schema_json = schema_pseudo_json

        try:
            schema = UApiSchema.from_json(schema_json)
            if extend_schema_json:
                UApiSchema.extend(schema, extend_schema_json)
            return Message({}, {"Ok": {}})
        except UApiSchemaParseError as e:
            e.printStackTrace()
            return Message({}, {"ErrorValidationFailure": {"cases": e.schema_parse_failures_pseudo_json}})

    options = Server.Options()
    options.onError = lambda e: print(e)  # Error handling
    server = Server(u_api, handler, options)

    def handle_message(msg: Any, timers: Summary, server: Server, connection: Any, frontdoor_topic: str) -> None:
        request_bytes = msg.get_data()

        print(f"    ->S {request_bytes}")

        @timers.time()
        def s():
            return server.process(request_bytes)

        response_bytes = s()

        print(f"    <-S {response_bytes}")
        connection.publish(msg.get_reply_to(), response_bytes)

    dispatcher = connection.subscribe(frontdoor_topic, lambda msg: handle_message(
        msg, timers, server, connection, frontdoor_topic))

    return dispatcher


def start_test_server(connection: NatsClient, metrics: CollectorRegistry, api_schema_path: str, frontdoor_topic: str, backdoor_topic: str) -> Subscription:
    json_data = Path(api_schema_path).read_text()
    u_api = UApiSchema.from_json(json_data)
    alternate_u_api = UApiSchema.extend(u_api, """
            [
                {
                    "struct.BackwardsCompatibleChange": {}
                }
            ]
            """)

    timers = Summary(frontdoor_topic, registry=metrics)

    serve_alternate_server = False

    class ThisError(RuntimeError):
        pass

    def handler(request_message: Message) -> Message:
        nonlocal serve_alternate_server
        try:
            request_headers = request_message.header
            request_body = request_message.body
            request_pseudo_json = [request_headers, request_body]
            request_bytes = json.dumps(request_pseudo_json).encode('utf-8')

            print(f"    <-s {request_bytes}")

            try:
                nats_response_message = connection.request(
                    backdoor_topic, request_bytes, timedelta(seconds=5))
            except Exception as e:
                raise RuntimeError(e)

            response_bytes = nats_response_message.get_data()

            print(f"    ->s {response_bytes}")

            response_pseudo_json = json.loads(response_bytes.decode('utf-8'))
            response_headers = response_pseudo_json[0]
            response_body = response_pseudo_json[1]

            toggle_alternate_server = request_headers.get(
                "_toggleAlternateServer")
            if toggle_alternate_server == True:
                serve_alternate_server = not serve_alternate_server

            throw_error = request_headers.get("_throwError")
            if throw_error == True:
                raise ThisError()

            return Message(response_headers, response_body)
        except Exception as e:
            raise RuntimeError(e)

    options = Server.Options()
    options.onError = lambda e: print(e)  # Error handling
    options.onRequest = lambda m: None  # onRequest handling
    options.onResponse = lambda m: None  # onResponse handling

    server = Server(u_api, handler, options)
    alternate_options = Server.Options()
    alternate_options.onError = lambda e: print(e)  # Error handling
    alternate_server = Server(alternate_u_api, handler, alternate_options)

    def handle_test_message(msg: Any, timers: Any, server: Server, alternate_server: Server, connection: Any, frontdoor_topic: str) -> None:
        nonlocal serve_alternate_server
        request_bytes = msg.get_data()

        print(f"    ->S {request_bytes}")

        @timers.time()
        def s():
            if serve_alternate_server:
                return alternate_server.process(request_bytes)
            else:
                return server.process(request_bytes)

        response_bytes = s()

        print(f"    <-S {response_bytes}")
        connection.publish(msg.get_reply_to(), response_bytes)

    dispatcher = connection.subscribe(frontdoor_topic, cb=lambda msg: handle_test_message(
        msg, timers, server, alternate_server, connection, frontdoor_topic))

    print(f"Test server listening on {frontdoor_topic}")

    return dispatcher


async def run_dispatcher_server():
    nats_url = os.getenv("NATS_URL")
    if nats_url is None:
        raise RuntimeError("NATS_URL env var not set")

    nats_options = {
        "servers": [nats_url],
    }

    done = asyncio.get_running_loop().create_future()

    metrics = CollectorRegistry()
    metrics_file = "./metrics/metrics.txt"

    servers: dict[str, Subscription] = {}

    def publish_metrics():
        with open(metrics_file, "w") as f:
            f.write(generate_latest(metrics).decode("utf-8"))

    connection = NatsClient()
    await connection.connect(**nats_options)

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

            with histogram.time():
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
                    server = start_test_server(
                        connection, metrics, api_schema_path, frontdoor_topic, backdoor_topic)
                    servers[server_id] = server
                elif target == "StartClientServer":
                    server_id = payload["id"]
                    client_frontdoor_topic = payload["clientFrontdoorTopic"]
                    client_backdoor_topic = payload["clientBackdoorTopic"]
                    use_binary = payload.get("useBinary", False)
                    server = start_client_test_server(
                        connection, metrics, client_frontdoor_topic, client_backdoor_topic, use_binary)
                    servers[server_id] = server
                elif target == "StartMockServer":
                    server_id = payload["id"]
                    api_schema_path = payload["apiSchemaPath"]
                    frontdoor_topic = payload["frontdoorTopic"]
                    config = payload["config"]
                    server = start_mock_test_server(
                        connection, metrics, api_schema_path, frontdoor_topic, config)
                    servers[server_id] = server
                elif target == "StartSchemaServer":
                    server_id = payload["id"]
                    api_schema_path = payload["apiSchemaPath"]
                    frontdoor_topic = payload["frontdoorTopic"]
                    server = start_schema_test_server(
                        connection, metrics, api_schema_path, frontdoor_topic)
                    servers[server_id] = server
                else:
                    raise RuntimeError("no matching server")

            response_bytes = json.dumps([{}, {"Ok": {}}]).encode("utf-8")

        except Exception as e:
            print(e)
            try:
                response_bytes = json.dumps(
                    [{}, {"ErrorUnknown": {}}]).encode("utf-8")
            except json.JSONDecodeError as e1:
                raise RuntimeError()

        print(f"    <-S {response_bytes.decode('utf-8')}")
        await connection.publish(msg.reply, response_bytes)

    dispatcher = await connection.subscribe("python", cb=message_handler)

    await done

    publish_metrics()

    print("Dispatcher exiting")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_dispatcher_server())
