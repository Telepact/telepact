from typing import List, Dict, Union, Any
from functools import reduce


class BinaryEncoder:
    def __init__(self, binary_encoding: Dict[str, int], binary_hash: Any) -> None:
        self.encode_map: Dict[str, int] = binary_encoding
        self.decode_map: Dict[int, str] = {
            v: k for k, v in binary_encoding.items()}
        self.binary_hash: Any = binary_hash

    def encode(self, japi_message: List[Any]) -> List[Any]:
        encoded_message_type = self.get(self.encode_map, japi_message[0])
        headers = japi_message[1]
        encoded_body = self.encode_keys(japi_message[2])
        return [encoded_message_type, headers, encoded_body]

    def decode(self, japi_message: List[Any]) -> List[Any]:
        encoded_message_type = japi_message[0]
        if isinstance(encoded_message_type, int):
            encoded_message_type = int(encoded_message_type)
        decoded_message_type = self.get(self.decode_map, encoded_message_type)
        headers = japi_message[1]
        given_hash = headers.get("_bin")
        decoded_body = self.decode_keys(japi_message[2])
        if self.binary_hash is not None and given_hash != self.binary_hash:
            raise IncorrectBinaryHashException()
        return [decoded_message_type, headers, decoded_body]

    def encode_keys(self, given: Any) -> Any:
        if given is None:
            return given
        elif isinstance(given, dict):
            new_map = {}
            for key, value in given.items():
                if isinstance(key, str):
                    try:
                        key = int(key)
                    except ValueError:
                        pass
                if key in self.encode_map:
                    key = self.get(self.encode_map, key)
                encoded_value = self.encode_keys(value)
                new_map[key] = encoded_value
            return new_map
        elif isinstance(given, list):
            return [self.encode_keys(item) for item in given]
        else:
            return given

    def decode_keys(self, given: Any) -> Any:
        if isinstance(given, dict):
            new_map = {}
            for key, value in given.items():
                if isinstance(key, str):
                    try:
                        key = int(key)
                    except ValueError:
                        pass
                if key in self.decode_map:
                    key = self.get(self.decode_map, key)
                encoded_value = self.decode_keys(value)
                new_map[key] = encoded_value
            return new_map
        elif isinstance(given, list):
            return [self.decode_keys(item) for item in given]
        else:
            return given

    def get(self, dictionary: Dict[Union[str, int], Any], key: Union[str, int]) -> Any:
        value = dictionary.get(key)
        if value is None:
            raise Exception("Missing encoding for " + str(key))
        return value
