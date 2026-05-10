from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter_ns
from typing import Any, Callable
from uuid import uuid4

import nats
from google.protobuf import descriptor_pb2, descriptor_pool, json_format, message_factory
from telepact import Client, FunctionRouter, Message, Server, TelepactSchema
from telepact.internal.HandleMessage import handle_message
from telepact.internal.ParseRequestMessage import parse_request_message

METRIC_HEADERS = {
    'request_transit': 'x-request-transit-ns',
    'server_deserialize': 'x-server-request-deserialize-ns',
    'server_serialize': 'x-server-response-serialize-ns',
    'server_sent': 'x-server-sent-ns',
}


@dataclass
class CaseDefinition:
    data_shape: str
    collection_shape: str
    telepact_function: str
    envelope_field: str
    payload: dict[str, Any]


@dataclass
class BenchCase:
    method: str
    data_shape: str
    collection_shape: str
    subject: str
    run: Callable[[], Any]
    finish: Callable[[], Any]


class PlainJsonCodec:
    def __init__(self, envelope_field: str, payload: dict[str, Any]) -> None:
        self.envelope_field = envelope_field
        self.request_object = {envelope_field: payload}
        self.response_object = {envelope_field: payload}

    def encode_request(self) -> bytes:
        return json.dumps(self.request_object, separators=(',', ':')).encode()

    def decode_request(self, data: bytes) -> dict[str, Any]:
        message = json.loads(data)
        if list(message.keys()) != [self.envelope_field]:
            raise ValueError('unexpected plain json request envelope')
        return message

    def encode_response(self) -> bytes:
        return json.dumps(self.response_object, separators=(',', ':')).encode()

    def decode_response(self, data: bytes) -> dict[str, Any]:
        message = json.loads(data)
        if list(message.keys()) != [self.envelope_field]:
            raise ValueError('unexpected plain json response envelope')
        return message


class ProtobufCodec:
    def __init__(self, descriptor_set_path: Path, envelope_field: str, payload: dict[str, Any]) -> None:
        file_set = descriptor_pb2.FileDescriptorSet()
        file_set.ParseFromString(descriptor_set_path.read_bytes())
        pool = descriptor_pool.DescriptorPool()
        for file_proto in file_set.file:
            pool.Add(file_proto)
        self.request_cls = message_factory.GetMessageClass(pool.FindMessageTypeByName('telepact.performance.Request'))
        self.response_cls = message_factory.GetMessageClass(pool.FindMessageTypeByName('telepact.performance.Response'))
        self.envelope_field = envelope_field
        self.request_message = self.request_cls()
        self.response_message = self.response_cls()
        json_format.ParseDict({envelope_field: payload}, self.request_message)
        json_format.ParseDict({envelope_field: payload}, self.response_message)

    def encode_request(self) -> bytes:
        return self.request_message.SerializeToString()

    def decode_request(self, data: bytes) -> Any:
        message = self.request_cls()
        message.ParseFromString(data)
        if message.WhichOneof('body') != self.envelope_field:
            raise ValueError('unexpected protobuf request envelope')
        return message

    def encode_response(self) -> bytes:
        return self.response_message.SerializeToString()

    def decode_response(self, data: bytes) -> Any:
        message = self.response_cls()
        message.ParseFromString(data)
        if message.WhichOneof('body') != self.envelope_field:
            raise ValueError('unexpected protobuf response envelope')
        return message


async def build_telepact_case(
    client_connection: nats.aio.client.Client,
    server_connection: nats.aio.client.Client,
    schema: TelepactSchema,
    case: CaseDefinition,
    method: str,
) -> BenchCase:
    subject = f'telepact.performance.python.{uuid4().hex}'
    async def route(_name: str, _request: Message) -> Message:
        return Message({}, {'Ok_': case.payload})

    function_router = FunctionRouter({case.telepact_function: route})
    options = Server.Options()
    options.auth_required = False
    server = Server(schema, function_router, options)

    async def server_handler(msg: nats.aio.msg.Msg) -> None:
        request_transit = perf_counter_ns() - int(msg.headers['x-client-sent-ns'])
        deserialize_start = perf_counter_ns()
        request_message = parse_request_message(msg.data, server.serializer, schema, server.on_error)
        deserialize_duration = perf_counter_ns() - deserialize_start
        response_message = await handle_message(
            request_message,
            None,
            schema,
            server.middleware,
            server.function_router,
            server.on_error,
            server.on_auth,
        )
        serialize_start = perf_counter_ns()
        response_bytes = server.serializer.serialize(response_message)
        serialize_duration = perf_counter_ns() - serialize_start
        await server_connection.publish(
            msg.reply,
            response_bytes,
            headers={
                METRIC_HEADERS['request_transit']: str(request_transit),
                METRIC_HEADERS['server_deserialize']: str(deserialize_duration),
                METRIC_HEADERS['server_serialize']: str(serialize_duration),
                METRIC_HEADERS['server_sent']: str(perf_counter_ns()),
            },
        )

    subscription = await server_connection.subscribe(subject, cb=server_handler)
    await server_connection.flush()

    async def adapter(request_message: Message, serializer) -> Message:
        serialize_start = perf_counter_ns()
        request_bytes = serializer.serialize(request_message)
        client_request_serialize = perf_counter_ns() - serialize_start
        response = await client_connection.request(
            subject,
            request_bytes,
            timeout=30,
            headers={'x-client-sent-ns': str(perf_counter_ns())},
        )
        response_network_transit = perf_counter_ns() - int(response.headers[METRIC_HEADERS['server_sent']])
        deserialize_start = perf_counter_ns()
        response_message = serializer.deserialize(response.data)
        client_response_deserialize = perf_counter_ns() - deserialize_start
        return Message(
            {
                'clientRequestSerializeNs': client_request_serialize,
                'requestSizeBytes': len(request_bytes),
                'requestNetworkTransitNs': int(response.headers[METRIC_HEADERS['request_transit']]),
                'serverRequestDeserializeNs': int(response.headers[METRIC_HEADERS['server_deserialize']]),
                'serverResponseSerializeNs': int(response.headers[METRIC_HEADERS['server_serialize']]),
                'responseSizeBytes': len(response.data),
                'responseNetworkTransitNs': response_network_transit,
                'clientResponseDeserializeNs': client_response_deserialize,
            },
            response_message.body,
        )

    client_options = Client.Options()
    client_options.use_binary = method in {'telepact_binary', 'telepact_packed_binary'}
    client_options.always_send_json = method == 'telepact_json'
    client = Client(adapter, client_options)

    async def run_sample() -> dict[str, int]:
        headers: dict[str, object] = {}
        if method == 'telepact_packed_binary':
            headers['@pac_'] = True
        response_message = await client.request(Message(headers, {case.telepact_function: case.payload}))
        if response_message.body != {'Ok_': case.payload}:
            raise ValueError('unexpected telepact response body')
        return {k: int(v) for k, v in response_message.headers.items()}

    async def finish() -> None:
        await subscription.unsubscribe()
        await server_connection.flush()

    async def wrapped() -> Any:
        try:
            return await run_sample()
        finally:
            pass

    return BenchCase(method, case.data_shape, case.collection_shape, subject, wrapped, finish)


async def build_non_telepact_case(
    client_connection: nats.aio.client.Client,
    server_connection: nats.aio.client.Client,
    case: CaseDefinition,
    method: str,
    descriptor_set: Path,
) -> BenchCase:
    subject = f'telepact.performance.python.{uuid4().hex}'
    codec = PlainJsonCodec(case.envelope_field, case.payload) if method == 'plain_json' else ProtobufCodec(descriptor_set, case.envelope_field, case.payload)

    async def server_handler(msg: nats.aio.msg.Msg) -> None:
        request_transit = perf_counter_ns() - int(msg.headers['x-client-sent-ns'])
        deserialize_start = perf_counter_ns()
        codec.decode_request(msg.data)
        deserialize_duration = perf_counter_ns() - deserialize_start
        serialize_start = perf_counter_ns()
        response_bytes = codec.encode_response()
        serialize_duration = perf_counter_ns() - serialize_start
        await server_connection.publish(
            msg.reply,
            response_bytes,
            headers={
                METRIC_HEADERS['request_transit']: str(request_transit),
                METRIC_HEADERS['server_deserialize']: str(deserialize_duration),
                METRIC_HEADERS['server_serialize']: str(serialize_duration),
                METRIC_HEADERS['server_sent']: str(perf_counter_ns()),
            },
        )

    subscription = await server_connection.subscribe(subject, cb=server_handler)
    await server_connection.flush()

    async def run_sample() -> dict[str, int]:
        serialize_start = perf_counter_ns()
        request_bytes = codec.encode_request()
        client_request_serialize = perf_counter_ns() - serialize_start
        response = await client_connection.request(
            subject,
            request_bytes,
            timeout=30,
            headers={'x-client-sent-ns': str(perf_counter_ns())},
        )
        response_network_transit = perf_counter_ns() - int(response.headers[METRIC_HEADERS['server_sent']])
        deserialize_start = perf_counter_ns()
        codec.decode_response(response.data)
        client_response_deserialize = perf_counter_ns() - deserialize_start
        return {
            'clientRequestSerializeNs': client_request_serialize,
            'requestSizeBytes': len(request_bytes),
            'requestNetworkTransitNs': int(response.headers[METRIC_HEADERS['request_transit']]),
            'serverRequestDeserializeNs': int(response.headers[METRIC_HEADERS['server_deserialize']]),
            'serverResponseSerializeNs': int(response.headers[METRIC_HEADERS['server_serialize']]),
            'responseSizeBytes': len(response.data),
            'responseNetworkTransitNs': response_network_transit,
            'clientResponseDeserializeNs': client_response_deserialize,
        }

    async def finish() -> None:
        await subscription.unsubscribe()
        await server_connection.flush()

    return BenchCase(method, case.data_shape, case.collection_shape, subject, run_sample, finish)


async def execute_case(
    client_connection: nats.aio.client.Client,
    server_connection: nats.aio.client.Client,
    schema: TelepactSchema,
    case: CaseDefinition,
    method: str,
    warmup: int,
    iterations: int,
    descriptor_set: Path,
) -> dict[str, Any]:
    if method.startswith('telepact_'):
        bench = await build_telepact_case(client_connection, server_connection, schema, case, method)
    else:
        bench = await build_non_telepact_case(client_connection, server_connection, case, method, descriptor_set)
    try:
        for _ in range(warmup):
            await bench.run()
        samples = [await bench.run() for _ in range(iterations)]
    finally:
        await bench.finish()
    return {
        'method': method,
        'dataShape': case.data_shape,
        'collectionShape': case.collection_shape,
        'samples': samples,
    }


async def main_async(args: argparse.Namespace) -> None:
    payload_data = json.loads(Path(args.payloads).read_text())
    cases = [
        CaseDefinition(
            data_shape=case['dataShape'],
            collection_shape=case['collectionShape'],
            telepact_function=case['telepactFunction'],
            envelope_field=case['envelopeField'],
            payload=case['payload'],
        )
        for case in payload_data['cases']
    ]
    schema = TelepactSchema.from_directory(args.schema_dir)
    client_connection = await nats.connect(args.nats_url)
    server_connection = await nats.connect(args.nats_url)
    try:
        results = []
        for method in ['telepact_json', 'telepact_binary', 'telepact_packed_binary', 'protobuf', 'plain_json']:
            for case in cases:
                results.append(
                    await execute_case(
                        client_connection,
                        server_connection,
                        schema,
                        case,
                        method,
                        args.warmup,
                        args.iterations,
                        Path(args.descriptor_set),
                    )
                )
        Path(args.output).write_text(
            json.dumps(
                {
                    'language': 'python',
                    'natsUrl': args.nats_url,
                    'warmupIterations': args.warmup,
                    'measuredIterations': args.iterations,
                    'cases': results,
                },
                indent=2,
            )
            + '\n'
        )
    finally:
        await client_connection.close()
        await server_connection.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--nats-url', required=True)
    parser.add_argument('--warmup', type=int, required=True)
    parser.add_argument('--iterations', type=int, required=True)
    parser.add_argument('--payloads', required=True)
    parser.add_argument('--schema-dir', required=True)
    parser.add_argument('--descriptor-set', required=True)
    parser.add_argument('--output', required=True)
    return parser.parse_args()


if __name__ == '__main__':
    asyncio.run(main_async(parse_args()))
