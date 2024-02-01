from dataclasses import dataclass
import uapi
import uapi._util
from typing import List, Dict
import uapi.types as types
import inspect


class _SchemaParseFailure:
    def __init__(self, path: List[object], reason: str, data: Dict[str, object]):
        self.path = path
        self.reason = reason
        self.data = data


def _find_stack() -> str:
    i = 0
    for stack in inspect.stack():
        i += 1
        if i == 1:
            continue
        stack_str = f'{stack}'
        if not '_util_types.py' in stack_str:
            return f'{stack.function}'


class _RandomGenerator:
    def __init__(self, collection_length_min: int, collection_length_max: int):
        self.seed = 0
        self.collection_length_min = collection_length_min
        self.collection_length_max = collection_length_max
        self.count = 0

    def set_seed(self, seed: int):
        self.seed = seed

    def next_int(self) -> int:
        self.seed = (self.seed * 1_103_515_245 + 12_345) & 0x7fffffff
        self.count += 1
        return self.seed

    def next_int_with_ceiling(self, ceiling: int) -> int:
        if ceiling == 0:
            return 0
        return self.next_int() % ceiling

    def next_boolean(self) -> bool:
        return self.next_int_with_ceiling(31) > 15

    def next_string(self) -> str:
        import base64
        import struct
        bytes_data = struct.pack(">i", self.next_int())
        return base64.b64encode(bytes_data).decode().rstrip("=")

    def next_double(self) -> float:
        # max = (2 << 31) - 1
        # half = (2 << 30)
        # quarter = (2 << 29)
        # x = float((self.next_int_with_ceiling(half) + quarter) & 0xFFFFFFFF)
        # y = float(max)
        return float(self.next_int() & 0x7fffffff) / float(0x7fffffff)

    def next_collection_length(self) -> int:
        return self.next_int_with_ceiling(self.collection_length_max - self.collection_length_min) + self.collection_length_min


class _ValidationFailure:
    def __init__(self, path: List[object], reason: str, data: Dict[str, object]):
        self.path = path
        self.reason = reason
        self.data = data


class _UType:
    def get_type_parameter_count(self) -> int:
        raise NotImplementedError

    def validate(self, value: object, type_parameters: List['_UTypeDeclaration'], generics: List['_UTypeDeclaration']) -> List[_ValidationFailure]:
        raise NotImplementedError

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, type_parameters: List['_UTypeDeclaration'], generics: List['_UTypeDeclaration'], random_generator: _RandomGenerator) -> object:
        raise NotImplementedError

    def get_name(self, generics: List['_UTypeDeclaration']) -> str:
        raise NotImplementedError


class _UTypeDeclaration:
    def __init__(self, type: _UType, nullable: bool, type_parameters: List['_UTypeDeclaration']):
        self.type = type
        self.nullable = nullable
        self.type_parameters = type_parameters

    def validate(self, value: object, generics: List['_UTypeDeclaration']) -> List[_ValidationFailure]:
        return uapi._util.validate_value_of_type(value, generics, self.type, self.nullable, self.type_parameters)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, generics: List['_UTypeDeclaration'], random_generator: _RandomGenerator) -> object:
        return uapi._util.generate_random_value_of_type(blueprint_value, use_blueprint_value, include_random_optional_fields, generics, random_generator, self.type, self.nullable, self.type_parameters)


class _UFieldDeclaration:
    def __init__(self, field_name: str, type_declaration: _UTypeDeclaration, optional: bool):
        self.field_name = field_name
        self.type_declaration = type_declaration
        self.optional = optional


class _UGeneric(_UType):
    def __init__(self, index: int):
        self.index = index

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration]) -> List[_ValidationFailure]:
        type_declaration = generics[self.index]
        return type_declaration.validate(value, [])

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration], random_generator: _RandomGenerator) -> object:
        generic_type_declaration = generics[self.index]
        return generic_type_declaration.generate_random_value(blueprint_value, use_blueprint_value, include_random_optional_fields, [], random_generator)

    def get_name(self, generics: List[_UTypeDeclaration]) -> str:
        type_declaration = generics[self.index]
        return type_declaration.type.get_name(generics)


class _UAny(_UType):
    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration]) -> List[_ValidationFailure]:
        return []

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration], random_generator: _RandomGenerator) -> object:
        return uapi._util.generate_random_any(random_generator)

    def get_name(self, generics: List[_UTypeDeclaration]) -> str:
        return uapi._util._ANY_NAME


class _UBoolean(_UType):
    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration]) -> List[_ValidationFailure]:
        return uapi._util.validate_boolean(value)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration], random_generator: _RandomGenerator) -> object:
        return uapi._util.generate_random_boolean(blueprint_value, use_blueprint_value, random_generator)

    def get_name(self, generics: List[_UTypeDeclaration]) -> str:
        return uapi._util._BOOLEAN_NAME


class _UInteger(_UType):
    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration]) -> List[_ValidationFailure]:
        return uapi._util.validate_integer(value)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration], random_generator: _RandomGenerator) -> object:
        return uapi._util.generate_random_integer(blueprint_value, use_blueprint_value, random_generator)

    def get_name(self, generics: List[_UTypeDeclaration]) -> str:
        return uapi._util._INTEGER_NAME


class _UNumber(_UType):
    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration]) -> List[_ValidationFailure]:
        return uapi._util.validate_number(value)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration], random_generator: _RandomGenerator) -> object:
        return uapi._util.generate_random_number(blueprint_value, use_blueprint_value, random_generator)

    def get_name(self, generics: List[_UTypeDeclaration]) -> str:
        return uapi._util._NUMBER_NAME


class _UString(_UType):
    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration]) -> List[_ValidationFailure]:
        return uapi._util.validate_string(value)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration], random_generator: _RandomGenerator) -> object:
        return uapi._util.generate_random_string(blueprint_value, use_blueprint_value, random_generator)

    def get_name(self, generics: List[_UTypeDeclaration]) -> str:
        return uapi._util._STRING_NAME


class _UArray(_UType):
    def get_type_parameter_count(self) -> int:
        return 1

    def validate(self, value: object, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration]) -> List[_ValidationFailure]:
        return uapi._util.validate_array(value, type_parameters, generics)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration], random_generator: _RandomGenerator) -> object:
        return uapi._util.generate_random_array(blueprint_value, use_blueprint_value, include_random_optional_fields, type_parameters, generics, random_generator)

    def get_name(self, generics: List[_UTypeDeclaration]) -> str:
        return uapi._util._ARRAY_NAME


class _UObject(_UType):
    def get_type_parameter_count(self) -> int:
        return 1

    def validate(self, value: object, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration]) -> List[_ValidationFailure]:
        return uapi._util.validate_object(value, type_parameters, generics)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration], random_generator: _RandomGenerator) -> object:
        return uapi._util.generate_random_object(blueprint_value, use_blueprint_value, include_random_optional_fields, type_parameters, generics, random_generator)

    def get_name(self, generics: List[_UTypeDeclaration]) -> str:
        return uapi._util._OBJECT_NAME


class _UStruct(_UType):
    def __init__(self, name: str, fields: Dict[str, _UFieldDeclaration], type_parameter_count: int):
        self.name = name
        self.fields = fields
        self.type_parameter_count = type_parameter_count

    def get_type_parameter_count(self) -> int:
        return self.type_parameter_count

    def validate(self, value: object, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration]) -> List[_ValidationFailure]:
        return uapi._util.validate_struct(value, type_parameters, generics, self.fields)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration], random_generator: _RandomGenerator) -> object:
        return uapi._util.generate_random_struct(blueprint_value, use_blueprint_value, include_random_optional_fields, type_parameters, generics, random_generator, self.fields)

    def get_name(self, generics: List[_UTypeDeclaration]) -> str:
        return uapi._util._STRUCT_NAME

    def __str__(self):
        return f'_UStruct(name: {self.name}, fields: {self.fields}, type_parameter_count: {self.type_parameter_count})'


class _UUnion(_UType):
    def __init__(self, name: str, cases: Dict[str, _UStruct], type_parameter_count: int):
        self.name = name
        self.cases = cases
        self.type_parameter_count = type_parameter_count

    def get_type_parameter_count(self) -> int:
        return self.type_parameter_count

    def validate(self, value: object, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration]) -> List[_ValidationFailure]:
        return uapi._util.validate_union(value, type_parameters, generics, self.cases)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration], random_generator: _RandomGenerator) -> object:
        return uapi._util.generate_random_union(blueprint_value, use_blueprint_value, include_random_optional_fields, type_parameters, generics, random_generator, self.cases)

    def get_name(self, generics: List[_UTypeDeclaration]) -> str:
        return uapi._util._UNION_NAME

    def __str__(self):
        return f'_UUnion(name: {self.name}, cases: {self.cases}, type_parameter_count: {self.type_parameter_count})'


class _UFn(_UType):
    def __init__(self, name: str, call: _UUnion, result: _UUnion, errors_regex: str):
        self.name = name
        self.call = call
        self.result = result
        self.errors_regex = errors_regex

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration]) -> List[_ValidationFailure]:
        return self.call.validate(value, type_parameters, generics)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration], random_generator: _RandomGenerator) -> object:
        return uapi._util.generate_random_fn(blueprint_value, use_blueprint_value, include_random_optional_fields, type_parameters, generics, random_generator, self.call.cases)

    def get_name(self, generics: List[_UTypeDeclaration]) -> str:
        return uapi._util._FN_NAME


class _UMockCall(_UType):
    def __init__(self, types: Dict[str, _UType]):
        self.types = types

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, given_obj: object, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration]) -> List[_ValidationFailure]:
        return uapi._util.validate_mock_call(given_obj, type_parameters, generics, self.types)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration], random_generator: _RandomGenerator) -> object:
        raise NotImplementedError("Not implemented")

    def get_name(self, generics: List[_UTypeDeclaration]) -> str:
        return uapi._util._MOCK_CALL_NAME


class _UMockStub(_UType):
    def __init__(self, types: Dict[str, _UType]):
        self.types = types

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, given_obj: object, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration]) -> List[_ValidationFailure]:
        return uapi._util.validate_mock_stub(given_obj, type_parameters, generics, self.types)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_random_optional_fields: bool, type_parameters: List[_UTypeDeclaration], generics: List[_UTypeDeclaration], random_generator: _RandomGenerator) -> object:
        raise NotImplementedError("Not implemented")

    def get_name(self, generics: List[_UTypeDeclaration]) -> str:
        return uapi._util._MOCK_STUB_NAME


class _UError:
    def __init__(self, name: str, errors: _UUnion):
        self.name = name
        self.errors = errors

    def __str__(self):
        return f'_UError(name: {self.name}, errors: {self.errors})'


class _DeserializationError(RuntimeError):
    def __init__(self, cause: Exception = None, message: str = None):
        super().__init__(message or cause)


class _BinaryEncoderUnavailableError(RuntimeError):
    pass


class _BinaryEncodingMissing(RuntimeError):
    def __init__(self, key: object):
        super().__init__(f"Missing binary encoding for {key}")


class _InvalidMessage(RuntimeError):
    pass


class _InvalidMessageBody(RuntimeError):
    pass


class _BinaryEncoding:
    def __init__(self, binary_encoding: Dict[str, int], checksum: int):
        self.encode_map = binary_encoding
        self.decode_map = {v: k for k, v in binary_encoding.items()}
        self.checksum = checksum


class _BinaryEncoder:
    def encode(self, message: List[object]) -> List[object]:
        raise NotImplementedError

    def decode(self, message: List[object]) -> List[object]:
        raise NotImplementedError


class _ServerBinaryEncoder(_BinaryEncoder):
    def __init__(self, binary_encoder: _BinaryEncoding):
        self.binary_encoder = binary_encoder

    def encode(self, message: List[object]) -> List[object]:
        return uapi._util.server_binary_encode(message, self.binary_encoder)

    def decode(self, message: List[object]) -> List[object]:
        return uapi._util.server_binary_decode(message, self.binary_encoder)


class _ClientBinaryEncoder(_BinaryEncoder):
    def __init__(self, binary_checksum_strategy: 'types.ClientBinaryStrategy'):
        self.recent_binary_encoders = {}
        self.binary_checksum_strategy = binary_checksum_strategy

    def encode(self, message: List[object]) -> List[object]:
        return uapi._util.client_binary_encode(message, self.recent_binary_encoders, self.binary_checksum_strategy)

    def decode(self, message: List[object]) -> List[object]:
        return uapi._util.client_binary_decode(message, self.recent_binary_encoders, self.binary_checksum_strategy)


class _MockStub:
    def __init__(self, when_function: str, when_argument: Dict[str, object], then_result: Dict[str, object], allow_argument_partial_match: bool, count: int):
        self.when_function = when_function
        self.when_argument = when_argument
        self.then_result = then_result
        self.allow_argument_partial_match = allow_argument_partial_match
        self.count = count


class _MockInvocation:
    def __init__(self, function_name: str, function_argument: Dict[str, object]):
        self.function_name = function_name
        self.function_argument = function_argument
        self.verified = False
