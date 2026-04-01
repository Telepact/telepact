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

from telepact import Client, Message, MockServer, MockTelepactSchema, Serializer


def create_mock_client() -> Client:
    mock_telepact_schema = MockTelepactSchema.from_directory('api')
    mock_server_options = MockServer.Options()
    mock_server_options.enable_message_response_generation = False
    mock_server = MockServer(mock_telepact_schema, mock_server_options)

    async def adapter(message: Message, serializer: Serializer) -> Message:
        request_bytes = serializer.serialize(message)
        response = await mock_server.process(request_bytes)
        return serializer.deserialize(response.bytes)

    return Client(adapter, Client.Options())


async def interact_with_mock_server() -> tuple[Message, Message]:
    client = create_mock_client()

    await client.request(Message({}, {
        'fn.createStub_': {
            'stub': {
                'fn.greet': {
                    'subject': 'Telepact',
                },
                '->': {
                    'Ok_': {
                        'message': 'Hello from the mock server!',
                    },
                },
            },
        },
    }))

    response = await client.request(Message({}, {
        'fn.greet': {
            'subject': 'Telepact',
        },
    }))
    verification = await client.request(Message({}, {
        'fn.verify_': {
            'call': {
                'fn.greet': {
                    'subject': 'Telepact',
                },
            },
        },
    }))
    return response, verification
