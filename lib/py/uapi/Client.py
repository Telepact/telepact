from typing import Callable, TYPE_CHECKING
from concurrent.futures import Future

from uapi.DefaultClientBinaryStrategy import DefaultClientBinaryStrategy
from uapi.DefaultSerialization import DefaultSerialization
from uapi.Serializer import Serializer
from uapi.internal.binary.ClientBinaryEncoder import ClientBinaryEncoder

if TYPE_CHECKING:
    from uapi.Message import Message


class Client:
    class Options:
        def __init__(self):
            self.use_binary = False
            self.timeout_ms_default = 5000
            self.serialization_impl = DefaultSerialization()
            self.binary_strategy = DefaultClientBinaryStrategy()

    def __init__(self, adapter: Callable[[Message, Serializer], Future[Message]], options: Options):
        self.adapter = adapter
        self.use_binary_default = options.use_binary
        self.timeout_ms_default = options.timeout_ms_default
        self.serializer = Serializer(
            options.serialization_impl, ClientBinaryEncoder(options.binary_strategy))

    def request(self, request_message: Message):
        from uapi.internal.ProcessRequestObject import process_request_object
        return process_request_object(request_message, self.adapter, self.serializer, self.timeout_ms_default, self.use_binary_default)
