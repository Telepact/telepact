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

from __future__ import annotations

from telepact import Client, Message, MockServer, MockTelepactSchema, Serializer


def build_mock_server() -> MockServer:
    options = MockServer.Options()
    options.generated_collection_length_min = 1
    options.generated_collection_length_max = 1
    options.randomize_optional_field_generation = False
    return MockServer(MockTelepactSchema.from_directory('api'), options)


def create_client(mock_server: MockServer) -> Client:
    async def adapter(message: Message, serializer: Serializer) -> Message:
        request_bytes = serializer.serialize(message)
        response = await mock_server.process(request_bytes)
        return serializer.deserialize(response.bytes)

    return Client(adapter, Client.Options())
