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

from typing import Callable, TYPE_CHECKING, Awaitable, Any
from concurrent.futures import Future

from .DefaultClientBinaryStrategy import DefaultClientBinaryStrategy
from .DefaultSerialization import DefaultSerialization
from .Serializer import Serializer
from .internal.binary.ClientBinaryEncoder import ClientBinaryEncoder

if TYPE_CHECKING:
    from .Message import Message


class Client:
    class Options:
        def __init__(self) -> None:
            self.use_binary = False
            self.always_send_json = True
            self.timeout_ms_default = 5000
            self.serialization_impl = DefaultSerialization()
            self.binary_strategy = DefaultClientBinaryStrategy()

    def __init__(self, adapter: Callable[['Message', 'Serializer'], Awaitable['Message']], options: 'Options'):
        self.adapter = adapter
        self.use_binary_default = options.use_binary
        self.always_send_json = options.always_send_json
        self.timeout_ms_default = options.timeout_ms_default
        self.serializer = Serializer(
            options.serialization_impl, ClientBinaryEncoder(options.binary_strategy))

    async def request(self, request_message: 'Message') -> 'Message':
        from .internal.ProcessRequestObject import process_request_object
        return await process_request_object(request_message, self.adapter, self.serializer, self.timeout_ms_default, self.use_binary_default, self.always_send_json)
