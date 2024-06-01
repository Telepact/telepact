from typing import Callable
from concurrent.futures import Future


class Options:
    def __init__(self):
        self.use_binary = False
        self.timeout_ms_default = 5000
        self.serialization_impl = DefaultSerializer()
        self.binary_strategy = DefaultClientBinaryStrategy()


class Client:
    def __init__(self, adapter: Callable[[Message, Serializer], Future[Message]], options: Options):
        self.adapter = adapter
        self.use_binary_default = options.use_binary
        self.timeout_ms_default = options.timeout_ms_default
        self.serializer = Serializer(
            options.serialization_impl, ClientBinaryEncoder(options.binary_strategy))

    def request(self, request_message: Message):
        return self.process_request_object(request_message, self.adapter, self.serializer, self.timeout_ms_default, self.use_binary_default)

    @staticmethod
    def process_request_object(request_message, adapter, serializer, timeout_ms_default, use_binary_default):
        pass
