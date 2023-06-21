from typing import List, Dict, Any, Callable, Union
import concurrent.futures

from client_process_error import ClientProcessError
from client_options import ClientOptions
from client import Client


class SyncClient(Client):
    class SyncTransport:
        def send(self, japi_message_payload: bytes) -> concurrent.futures.Future[bytes]:
            pass

    def __init__(self, sync_transport: SyncTransport, options: ClientOptions = ClientOptions()):
        super().__init__(options)
        self.sync_transport = sync_transport
        self.serializer = options.serializer
        self.timeout_ms = options.timeout_ms

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

            output_japi_message_payload = self.sync_transport.send(
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
