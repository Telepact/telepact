from typing import List, Dict, Any


class Client:
    def __init__(self, options: "ClientOptions") -> None:
        self.processor: "ClientProcessor" = options.processor
        self.use_binary: bool = options.use_binary
        self.binary_encoder_store: AtomicReference["BinaryEncoder"] = AtomicReference(
        )

    def call(self, function_name: str, headers: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        mutable_headers = HashMap(headers)
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
            binary_encoder = self.binary_encoder_store.get()
            if self.use_binary and binary_encoder is None:
                headers["_binaryStart"] = True

            output_japi_message = []
            if binary_encoder is not None:
                headers["_bin"] = binary_encoder.binary_hash
                encoded_input_japi_message = binary_encoder.encode(
                    input_japi_message)
                encoded_output_japi_message = self.serialize_and_transport(
                    encoded_input_japi_message, True)
                output_japi_message = binary_encoder.decode(
                    encoded_output_japi_message)
            else:
                output_japi_message = self.serialize_and_transport(
                    input_japi_message, False)

            output_headers = output_japi_message[1]
            if "_binaryEncoding" in output_headers:
                binary_hash = output_headers["_bin"]
                initial_binary_encoding = output_headers["_binaryEncoding"]
                binary_encoding = {
                    key: int(value) if isinstance(value, int) else value for key, value in initial_binary_encoding.items()
                }
                new_binary_encoder = BinaryEncoder(
                    binary_encoding, binary_hash)
                self.binary_encoder_store.set(new_binary_encoder)
                return new_binary_encoder.decode(output_japi_message)

            return output_japi_message
        except Exception as e:
            raise ClientProcessError(e)

    def serialize_and_transport(self, input_japi_message: List[Any], use_msg_pack: bool) -> List[Any]:
        # Implement this method in the derived class
        pass


class ClientOptions:
    def __init__(self, processor: "ClientProcessor", use_binary: bool) -> None:
        self.processor: "ClientProcessor" = processor
        self.use_binary: bool = use_binary


class ClientProcessor:
    def process(self, input_japi_message: List[Any], proceed: "Callable[[List[Any]], List[Any]]") -> List[Any]:
        # Implement this method in the derived class
        pass


class BinaryEncoder:
    def __init__(self, binary_encoding: Dict[str, int], binary_hash: Any) -> None:
        self.binary_encoding: Dict[str, int] = binary_encoding
        self.binary_hash: Any = binary_hash

    def encode(self, input_data: Any) -> Any:
        # Implement the encoding logic
        pass

    def decode(self, encoded_data: Any) -> Any:
        # Implement the decoding logic
        pass
