from typing import Callable, List, Dict, Any, Union
from collections import OrderedDict
import base64
import random
import asyncio

from client import Client
from client_process_error import ClientProcessError
from client_options import ClientOptions


class AsyncClient(Client):
    class Cache(OrderedDict):
        def __init__(self, max_size: int):
            super().__init__()
            self.max_size = max_size

        def __setitem__(self, key, value):
            if len(self) >= self.max_size:
                oldest_key = next(iter(self))
                del self[oldest_key]
            super().__setitem__(key, value)

    async def send(self, japi_message_payload: bytes):
        # Implement your async transport logic here
        pass

    def __init__(self, async_transport: Callable[[bytes], None], options: ClientOptions = ClientOptions()):
        super().__init__(options)
        self.async_transport = async_transport
        self.serializer = options.serializer
        self.timeout_ms = options.timeout_ms
        self.waiting_requests = self.Cache(256)

    async def serialize_and_transport(self, input_japi_message: List[Any], use_msg_pack: bool) -> List[Any]:
        try:
            id_ = self.generate_32_bit_id()

            headers = input_japi_message[1]
            headers["_id"] = id_
            headers["_timeout_ms"] = self.timeout_ms

            future = asyncio.Future()
            self.waiting_requests[id_] = future

            if use_msg_pack:
                input_japi_message_payload = self.serializer.serialize_to_msg_pack(
                    input_japi_message)
            else:
                input_japi_message_payload = self.serializer.serialize_to_json(
                    input_japi_message)

            await self.async_transport(input_japi_message_payload)

            return await asyncio.wait_for(future, timeout=self.timeout_ms / 1000)
        except Exception as e:
            raise ClientProcessError(e)

    def receive_output_japi_message(self, output_japi_message_payload: bytes):
        try:
            if output_japi_message_payload[0] == ord('['):
                output_japi_message = self.serializer.deserialize_from_json(
                    output_japi_message_payload)
            else:
                output_japi_message = self.serializer.deserialize_from_msg_pack(
                    output_japi_message_payload)

            headers = output_japi_message[1]
            id_ = headers["_id"]

            self.waiting_requests[id_].set_result(output_japi_message)
            del self.waiting_requests[id_]
        except Exception as e:
            raise ClientProcessError(e)

    def generate_32_bit_id(self) -> str:
        random_bytes = random.getrandbits(32).to_bytes(4, "big")
        return base64.urlsafe_b64encode(random_bytes).rstrip(b"=").decode("ascii")
