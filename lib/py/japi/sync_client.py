from typing import List, Dict, Any, Callable, Union
import concurrent.futures

from japi.client_process_error import ClientProcessError
from japi.client import Client
from japi.default_serializer import DefaultSerializer
from japi.serializer import Serializer


class SyncClient(Client):

    def __init__(self, sync_transport: Callable[[bytes], concurrent.futures.Future[bytes]], timeout_ms: int = 5000, serializer: Serializer = DefaultSerializer(), use_binary: bool = False, force_send_json: bool = True):
        super().__init__(use_binary=use_binary, force_send_json=force_send_json)
        self.sync_transport = sync_transport
        self.serializer = serializer
        self.timeout_ms = timeout_ms

    def serialize_and_transport(
        self, input_japi_message: List[Any], use_msg_pack: bool
    ) -> List[Any]:
        try:
            if use_msg_pack:
                input_japi_message_payload = self.serializer.serialize_to_msg_pack(
                    input_japi_message
                )
            else:
                input_japi_message_payload = self.serializer.serialize_to_json(
                    input_japi_message
                )

            output_japi_message_payload = self.sync_transport(
                input_japi_message_payload
            ).result(self.timeout_ms / 1000)

            output_japi_message: List[Any]
            if output_japi_message_payload[0] == ord('['):
                output_japi_message = self.serializer.deserialize_from_json(
                    output_japi_message_payload
                )
            else:
                output_japi_message = self.serializer.deserialize_from_msg_pack(
                    output_japi_message_payload
                )

            return output_japi_message
        except Exception as e:
            raise ClientProcessError(e)
