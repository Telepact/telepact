import hashlib
from typing import Dict, Union


class BinaryEncoder:
    def __init__(self, encode_map: Dict[str, int], binary_hash: int):
        self.encode_map = encode_map
        self.binary_hash = binary_hash


class FunctionDefinition:
    pass


class TypeDefinition:
    pass


class Struct:
    pass


class Enum:
    pass


class ErrorDefinition:
    pass


def build(definitions: Dict[str, Union[FunctionDefinition, TypeDefinition, ErrorDefinition]]) -> BinaryEncoder:
    all_keys = set()
    for key, definition in definitions.items():
        all_keys.add(key)
        if isinstance(definition, FunctionDefinition):
            all_keys.update(definition.inputStruct().fields().keys())
            all_keys.update(definition.outputStruct().fields().keys())
            all_keys.update(definition.errors())
        elif isinstance(definition, TypeDefinition):
            type = definition.type()
            if isinstance(type, Struct):
                all_keys.update(type.fields().keys())
            elif isinstance(type, Enum):
                all_keys.update(type.cases().keys())
        elif isinstance(definition, ErrorDefinition):
            all_keys.update(definition.fields().keys())

    i = 0
    binary_encoding = {}
    for key in sorted(all_keys):
        binary_encoding[key] = i
        i += 1

    final_string = '\n'.join(all_keys)
    binary_hash = int(hashlib.sha256(
        final_string.encode('utf-8')).hexdigest(), 16)

    return BinaryEncoder(binary_encoding, binary_hash)
