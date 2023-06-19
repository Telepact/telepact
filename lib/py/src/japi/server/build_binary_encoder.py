from typing import Dict, Union, List
from hashlib import sha256
import struct


class BinaryEncoder:
    def __init__(self, binary_encoding: Dict[str, int], binary_hash: int):
        self.binary_encoding = binary_encoding
        self.binary_hash = binary_hash


def build(definitions: Dict[str, Union[FunctionDefinition, TypeDefinition, ErrorDefinition]]) -> BinaryEncoder:
    all_keys = set()
    for key, value in definitions.items():
        all_keys.add(key)
        if isinstance(value, FunctionDefinition):
            f = value
            all_keys.update(f.input_struct().fields().keys())
            all_keys.update(f.output_struct().fields().keys())
            all_keys.update(f.errors())
        elif isinstance(value, TypeDefinition):
            t = value
            type_value = t.type()
            if isinstance(type_value, Struct):
                o = type_value
                all_keys.update(o.fields().keys())
            elif isinstance(type_value, Enum):
                u = type_value
                all_keys.update(u.cases().keys())
        elif isinstance(value, ErrorDefinition):
            e = value
            all_keys.update(e.fields().keys())

    i = 0
    binary_encoding = {}
    for key in sorted(all_keys):
        binary_encoding[key] = i
        i += 1

    final_string = "\n".join(sorted(all_keys))
    binary_hash = int.from_bytes(sha256(final_string.encode(
        'utf-8')).digest(), byteorder='big', signed=False)

    return BinaryEncoder(binary_encoding, binary_hash)
