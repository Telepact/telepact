# 27. TDD with TestClient

Let's test our own Telepact server directly, without even starting HTTP.

## Install what this example needs

```sh
pip install --pre telepact pytest
```

## Reuse the minimum server, but leave one bug in it

Create `server.py`:

```py
from telepact import FunctionRouter, Message, Server, TelepactSchema


schema = TelepactSchema.from_directory('./api')

options = Server.Options()


async def hello(function_name: str, request_message: Message) -> Message:
    name = request_message.body[function_name]['name']
    return Message({}, {'Ok_': {'message': name}})


function_router = FunctionRouter()
function_router.register_unauthenticated_routes({'fn.hello': hello})
telepact_server = Server(schema, function_router, options)
```

That is intentionally wrong. We want `Hello, Telepact!`, but the server only
returns `Telepact`.

## Point a client at `telepact_server.process(...)`

Create `test_server.py`:

```py
import asyncio

import pytest

from telepact import Client, Message, Serializer, TestClient
from server import telepact_server


async def adapter(message: Message, serializer: Serializer) -> Message:
    request_bytes = serializer.serialize(message)
    response = await telepact_server.process(request_bytes)
    return serializer.deserialize(response.bytes)


def make_test_client() -> TestClient:
    client = Client(adapter, Client.Options())
    return TestClient(client, TestClient.Options())


def test_hello_shows_the_actual_payload() -> None:
    test_client = make_test_client()

    with pytest.raises(AssertionError) as error_info:
        asyncio.run(
            test_client.assert_request(
                Message({}, {'fn.hello': {'name': 'Telepact'}}),
                {'Ok_': {'message': 'Hello, Telepact!'}},
                True,
            )
        )

    assert "Actual: {'Ok_': {'message': 'Telepact'}}" in str(error_info.value)


def test_hello_can_keep_going_with_multiple_assertions() -> None:
    test_client = make_test_client()

    response = asyncio.run(
        test_client.assert_request(
            Message({}, {'fn.hello': {'name': 'Telepact'}}),
            {'Ok_': {'message': 'Hello, Telepact!'}},
            False,
        )
    )

    greeting = response.body['Ok_']['message']

    assert greeting.startswith('Hello, ')
    extracted_name = greeting.removeprefix('Hello, ')
    assert extracted_name == 'Telepact!'
```

## Run the tests

```sh
pytest -q
```

The first test is the usual red phase: the assertion fails, and the error text
includes the actual payload that came back from the server.

The second test shows the more unusual part. It uses `expect_match=False`,
which means we currently expect the server to *not* match yet. In that case,
`TestClient` returns a schema-valid response built from the expected payload we
supplied, so the test can keep going.

That matters when one assertion depends on the result of an earlier one. Here,
the server really returned `Telepact`, but `TestClient` hands the test a
response whose `message` still satisfies the expected shape. That lets us first
assert `startswith('Hello, ')` and then use that result for the next assertion
on `Telepact!`, all in one red-phase test.

## Fix the server

Once we are ready to make the test green, change the handler:

```py
async def hello(function_name: str, request_message: Message) -> Message:
    name = request_message.body[function_name]['name']
    return Message({}, {'Ok_': {'message': f'Hello, {name}!'}})
```

Now we can switch back to `expect_match=True` and keep the strict assertion.

Next: [28. Best practices for server implementers](./28-server-best-practices.md)
