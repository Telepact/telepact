from typing import List, Dict, Union, Any
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from japi.binary_encoder import BinaryEncoder
from japi.client_error import ClientError
from japi.client_process_error import ClientProcessError

from japi.client_processor import ClientProcessor
from japi.client_options import ClientOptions


class Client:
    def __init__(self, options: ClientOptions) -> None:
        self.processor: ClientProcessor = options.processor
        self.use_binary: bool = options.use_binary
        self.force_send_json: bool = options.force_send_json
        self.binary_encoder_store: deque[BinaryEncoder] = deque()

    def call(self, function_name: str, headers: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        mutable_headers = headers.copy()
        message_type = f"function.{function_name}"
        input_japi_message = [message_type, mutable_headers, input_data]
        output_japi_message = self.processor.process(
            input_japi_message, self.proceed)

        output_message_type = output_japi_message[0]
        output_headers = output_japi_message[1]
        output = output_japi_message[2]

        if output_message_type.startswith("error."):
            raise ClientError(output_message_type, output)

        return output

    def proceed(self, input_japi_message: List[Any]) -> List[Any]:
        try:
            headers = input_japi_message[1]

            if self.use_binary:
                binary_checksums = [
                    binary_encoding.checksum for binary_encoding in self.binary_encoder_store]
                headers["_bin"] = binary_checksums

            binary_encoder = self.binary_encoder_store[0] if self.binary_encoder_store else None
            final_input_japi_message: List[Any]
            send_as_msg_pack = False
            if self.force_send_json or not self.use_binary or binary_encoder is None:
                final_input_japi_message = input_japi_message
            else:
                final_input_japi_message = binary_encoder.encode(
                    input_japi_message)
                send_as_msg_pack = True

            output_japi_message = self.serialize_and_transport(
                final_input_japi_message, send_as_msg_pack)
            output_headers = output_japi_message[1]

            if "_bin" in output_headers:
                binary_checksum = output_headers["_bin"]

                if "_binaryEncoding" in output_headers:
                    initial_binary_encoding = output_headers["_binaryEncoding"]
                    binary_encoding = {
                        key: int(value) if isinstance(value, int) else value
                        for key, value in initial_binary_encoding.items()
                    }
                    new_binary_encoder = BinaryEncoder(
                        binary_encoding, binary_checksum[0])
                    self.binary_encoder_store.append(new_binary_encoder)

                    if len(self.binary_encoder_store) >= 3:
                        self.binary_encoder_store.pop()

                output_binary_encoder = self.find_binary_encoder(
                    binary_checksum[0])

                return output_binary_encoder.decode(output_japi_message)

            return output_japi_message
        except Exception as e:
            raise ClientProcessError(e)

    def find_binary_encoder(self, checksum: int) -> BinaryEncoder:
        for binary_encoder in self.binary_encoder_store:
            if binary_encoder.checksum == checksum:
                return binary_encoder
        raise ClientProcessError(
            Exception("No matching encoding found, cannot decode binary"))

    def serialize_and_transport(self, input_japi_message: List[Any], use_msg_pack: bool) -> List[Any]:
        raise NotImplementedError(
            "Method serialize_and_transport must be implemented in a subclass.")
