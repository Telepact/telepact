from typing import List, Dict, Union

from japi.internal_types import IncorrectBinaryHashException


class BinaryEncoder:
    def __init__(self, binary_encoding: Dict[str, int], binary_hash: int) -> None:
        self.encode_map: Dict[str, int] = binary_encoding
        self.decode_map: Dict[int, str] = {
            int(v): k for k, v in binary_encoding.items()}
        self.checksum: int = binary_hash

    def encode(self, japi_message: List[object]) -> List[object]:
        encoded_message_type = self.get(self.encode_map, japi_message[0])
        headers = japi_message[1]
        encoded_body = self.encode_keys(japi_message[2])
        return [encoded_message_type, headers, encoded_body]

    def decode(self, japi_message: List[object]) -> List[object]:
        encoded_message_type = japi_message[0]
        if isinstance(encoded_message_type, int):
            encoded_message_type = int(encoded_message_type)
        decoded_message_type = self.get(self.decode_map, encoded_message_type)
        headers = japi_message[1]
        given_checksums = headers["_bin"]
        decoded_body = self.decode_keys(japi_message[2])
        if self.checksum is not None and self.checksum not in given_checksums:
            raise IncorrectBinaryHashException()
        return [decoded_message_type, headers, decoded_body]

    def encode_keys(self, given: Union[None, Dict[object, object], List[object]]) -> Union[None, Dict[object, object], List[object]]:
        if given is None:
            return given
        elif isinstance(given, dict):
            new_map = {}
            for key, value in given.items():
                if isinstance(key, str):
                    try:
                        key = int(key)
                    except Exception:
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

    def decode_keys(self, given: Union[Dict[object, object], List[object]]) -> Union[Dict[object, object], List[object]]:
        if isinstance(given, dict):
            new_map = {}
            for key, value in given.items():
                if isinstance(key, str):
                    try:
                        key = int(key)
                    except Exception:
                        pass
                if key in self.decode_map:
                    key = self.get(self.decode_map, key)
                decoded_value = self.decode_keys(value)
                new_map[key] = decoded_value
            return new_map
        elif isinstance(given, list):
            return [self.decode_keys(item) for item in given]
        else:
            return given

    def get(self, map: Dict[object, object], key: object) -> object:
        value = map.get(key)
        if value is None:
            raise RuntimeError("Missing encoding for " + str(key))
        return value
