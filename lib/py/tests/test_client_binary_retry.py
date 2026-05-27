import asyncio
import importlib
import json
from typing import Any


telepact = importlib.import_module("telepact")
Client = telepact.Client
FunctionRouter = telepact.FunctionRouter
Message = telepact.Message
Server = telepact.Server
TelepactSchema = telepact.TelepactSchema


def test_client_retries_stale_binary_using_refreshed_encoding() -> None:
    schema = TelepactSchema.from_json(
        json.dumps(
            [
                {
                    "fn.example": {},
                    "->": [
                        {
                            "Ok_": {}
                        }
                    ],
                }
            ]
        )
    )

    async def route(_function_name: str, _request_message: object) -> object:
        return Message({}, {"Ok_": {}})

    server_options = Server.Options()
    server_options.auth_required = False
    server = Server(schema, FunctionRouter({"fn.example": route}), server_options)

    request_bytes_sent: list[bytes] = []
    response_bytes_seen: list[bytes] = []

    async def adapter(message: object, serializer: Any) -> object:
        request_bytes = serializer.serialize(message)
        request_bytes_sent.append(request_bytes)
        response = await server.process(request_bytes)
        response_bytes_seen.append(response.bytes)
        return serializer.deserialize(response.bytes)

    client_options = Client.Options()
    client_options.use_binary = True
    client_options.always_send_json = False
    client = Client(adapter, client_options)

    serialization_impl = client.serializer.serialization_impl
    binary_encoding_cache = serialization_impl._client_binary_encoding_cache
    checksum_strategy = serialization_impl._client_binary_checksum_strategy
    binary_encoding_cache.add(999, {"fn.example": 0, "Ok_": 1})
    checksum_strategy.update_checksum(999)

    response_message = asyncio.run(client.request(Message({}, {"fn.example": {}})))

    assert response_message.body == {"Ok_": {}}
    assert len(request_bytes_sent) == 2
    assert request_bytes_sent[0][0] == 0x92
    assert request_bytes_sent[1][0] == 0x92
    assert response_bytes_seen[0][0] != 0x92
    assert response_bytes_seen[1][0] == 0x92