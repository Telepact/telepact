import asyncio
import importlib
import json

from telepact.TelepactError import TelepactError
from telepact.internal.validation.InvalidMessage import InvalidMessage

telepact = importlib.import_module("telepact")
FunctionRouter = telepact.FunctionRouter
Message = telepact.Message
Server = telepact.Server
TelepactSchema = telepact.TelepactSchema


class FailingDeserializer:
    def __init__(self) -> None:
        self.serialized_messages: list[object] = []

    def serialize(self, message: object) -> bytes:
        message = message
        self.serialized_messages.append(message)
        return json.dumps([message.headers, message.body]).encode()  # type: ignore[attr-defined]

    def deserialize(self, message_bytes: bytes) -> object:
        raise InvalidMessage()


def test_process_bytes_short_circuits_parse_failures() -> None:
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

    on_error_calls: list[TelepactError] = []
    on_request_calls: list[object] = []
    on_response_calls: list[object] = []
    middleware_calls: list[object] = []

    async def middleware(_request_message: object, _function_router: object) -> object:
        middleware_calls.append(_request_message)
        return Message({}, {"Ok_": {}})

    options = Server.Options()
    options.auth_required = False
    options.on_error = on_error_calls.append
    options.on_request = on_request_calls.append
    options.on_response = on_response_calls.append
    setattr(options, "middleware", middleware)

    server = Server(schema, FunctionRouter({}), options)
    serializer = FailingDeserializer()
    server.serializer = serializer  # type: ignore[assignment]

    response = asyncio.run(server.process(b"not valid telepact"))

    assert response.headers == {}
    assert on_request_calls == []
    assert on_response_calls == []
    assert middleware_calls == []
    assert len(on_error_calls) == 1

    assert serializer.serialized_messages == [
        Message({}, {"ErrorParseFailure_": {"reasons": [{"ExpectedJsonArrayOfTwoObjects": {}}]}})
    ]
    assert json.loads(response.bytes) == [
        {},
        {"ErrorParseFailure_": {"reasons": [{"ExpectedJsonArrayOfTwoObjects": {}}]}},
    ]


def test_process_bytes_reflects_recoverable_id_on_parse_failure() -> None:
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

    options = Server.Options()
    options.auth_required = False
    server = Server(schema, FunctionRouter({}), options)

    response = asyncio.run(
        server.process(b'[{"@id_": "request-123"}, {"fn.example": "wrong"}]')
    )

    assert response.headers == {"@id_": "request-123"}
    assert json.loads(response.bytes) == [
        {"@id_": "request-123"},
        {
            "ErrorParseFailure_": {
                "reasons": [{"ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject": {}}]
            }
        },
    ]