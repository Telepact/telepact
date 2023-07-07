from typing import Any, Dict, List, Optional, Union

from typing import Dict, List

from typing import Dict, List, Tuple

from japi.internal_types import *

from typing import Dict, Any
import re


from typing import Any, Dict, Union


from typing import Any, Dict, Union

from typing import List, Dict, Any

from typing import List, Callable, Dict, Any


from typing import Any, List, Dict, Callable, Tuple, Union
# Assuming BinaryEncoder is imported from another module
from japi.binary_encoder import BinaryEncoder
from japi.handler import Handler
from japi.serializer import Serializer
from japi.deserialization_error import DeserializationError
from japi.application_error import ApplicationError


def process(input_japi_message_payload: bytes,
            serializer: Serializer,
            on_error: Callable[[Exception], None],
            binary_encoder: BinaryEncoder,
            api_description: Dict[str, Definition],
            internal_handler: Handler,
            handler: Handler) -> bytes:
    input_japi_message: List[Any]
    input_is_binary = False

    if input_japi_message_payload[0] == ord('['):
        try:
            input_japi_message = serializer.deserialize_from_json(
                input_japi_message_payload)
        except DeserializationError as e:
            on_error(e)
            return serializer.serialize_to_json(["error._ParseFailure", {}, {}])
    else:
        try:
            encoded_input_japi_message = serializer.deserialize_from_msgpack(
                input_japi_message_payload)
            if len(encoded_input_japi_message) < 3:
                return serializer.serialize_to_json(["error._ParseFailure", {}, {"reason": "JapiMessageArrayMustHaveThreeElements"}])
            input_japi_message = binary_encoder.decode(
                encoded_input_japi_message)
            input_is_binary = True
        except IncorrectBinaryHashException as e:
            on_error(e)
            return serializer.serialize_to_json(["error._InvalidBinaryEncoding", {}, {}])
        except DeserializationError as e:
            on_error(e)
            return serializer.serialize_to_json(["error._ParseFailure", {}, {}])

    output_japi_message = process_object(input_japi_message, on_error, binary_encoder, api_description,
                                         internal_handler, handler)
    headers = output_japi_message[1]  # Assuming headers is a dictionary
    return_as_binary = "_bin" in headers

    if not return_as_binary and input_is_binary:
        headers["_bin"] = binary_encoder.binary_hash

    if input_is_binary or return_as_binary:
        encoded_output_japi_message = binary_encoder.encode(
            output_japi_message)
        return serializer.serialize_to_msg_pack(encoded_output_japi_message)
    else:
        return serializer.serialize_to_json(output_japi_message)


def process_object(input_japi_message: List[Any], on_error: Callable[[Exception], None],
                   binary_encoder: BinaryEncoder,
                   api_description: Dict[str, Definition], internal_handler: Handler, handler: Handler) -> List[Any]:
    final_headers: Dict[str, Any] = {}

    try:
        try:
            if len(input_japi_message) < 3:
                raise JapiMessageArrayTooFewElements()

            message_type: str = input_japi_message[0]
            if not isinstance(message_type, str):
                raise JapiMessageTypeNotString()

            regex = re.compile(r'^function\.([a-zA-Z_]\w*)(.input)?')
            matcher = regex.match(message_type)
            if not matcher:
                raise JapiMessageTypeNotFunction()
            function_name: str = matcher.group(1)

            headers: Dict[str, Any] = input_japi_message[1]
            if not isinstance(headers, dict):
                raise JapiMessageHeaderNotObject()

            if headers.get("_binaryStart") is True:
                # Client is initiating handshake for binary protocol
                final_headers["_bin"] = binary_encoder.binary_hash
                final_headers["_binaryEncoding"] = binary_encoder.encode_map

            # Reflect call id
            call_id = headers.get("_id")
            if call_id is not None:
                final_headers["_id"] = call_id

            input_data: Dict[str, Any] = input_japi_message[2]
            if not isinstance(input_data, dict):
                raise JapiMessageBodyNotObject()

            function_def = api_description.get(message_type)

            if isinstance(function_def, FunctionDefinition):
                function_definition: FunctionDefinition = function_def
            else:
                raise FunctionNotFound(function_name)

            sliced_types: Dict[str, List[str]] = None
            if "_sel" in headers:
                sliced_types = headers.get("_sel")
                if not isinstance(sliced_types, dict):
                    raise InvalidSelectFieldsHeader()
                for fields in sliced_types.values():
                    for field in fields:
                        # verify the cast works
                        string_field: str = field

            validate_struct(
                "input", function_definition.input_struct.fields, input_data)

            if function_name.startswith("_"):
                output_data = internal_handler(
                    function_name, headers, input_data)
            else:
                output_data = handler(
                    function_name, headers, input_data)

            if isinstance(output_data, ApplicationError):
                if output_data.message_type in function_definition.errors:
                    def_ = api_description.get(output_data.message_type)
                    if isinstance(def_, ErrorDefinition):
                        try:
                            validate_struct(
                                "error", def_.fields, output_data.body)
                        except Exception as e2:
                            raise InvalidApplicationFailure(e2)

                        raise output_data
                    else:
                        raise DisallowedError(output_data)

            validate_struct(
                "output", function_definition.output_struct.fields, output_data)

            final_output: Dict[str, Any]
            if sliced_types is not None:
                final_output = slice_types(
                    function_definition.output_struct, output_data, sliced_types)
            else:
                final_output = output_data

            output_message_type = f"function.{function_name}"

            return [output_message_type, final_headers, final_output]

        except Exception as e:
            try:
                on_error(e)
            except Exception:
                pass
            raise e

    except StructHasExtraFields as e:
        message_type = "error._InvalidRequestBody"
        errors = {
            f"{e.namespace}.{field}": "UnknownStructField" for field in e.extra_fields}
        message_body = create_invalid_fields(errors)

        return [message_type, final_headers, message_body]

    except StructMissingFields as e:
        message_type = "error._InvalidRequestBody"
        errors = {
            f"{e.namespace}.{field}": "RequiredStructFieldMissing" for field in e.missing_fields}
        message_body = create_invalid_fields(errors)

        return [message_type, final_headers, message_body]

    except UnknownEnumField as e:
        message_type = "error._InvalidRequestBody"
        message_body = create_invalid_field(
            f"{e.namespace}.{e.field}", "UnknownEnumField")

        return [message_type, final_headers, message_body]

    except EnumDoesNotHaveOnlyOneField as e:
        message_type = "error._InvalidRequestBody"
        message_body = create_invalid_field(
            e.namespace, "EnumDoesNotHaveExactlyOneField")

        return [message_type, final_headers, message_body]

    except InvalidFieldType as e:
        entry = create_invalid_field_full(e)

        message_type = entry[0]
        message_body = entry[1]

        return [message_type, final_headers, message_body]

    except (InvalidOutput, InvalidApplicationFailure):
        message_type = "error._InvalidResponseBody"

        return [message_type, final_headers, {}]

    except InvalidInput:
        message_type = "error._InvalidRequestBody"

        return [message_type, final_headers, {}]

    except (InvalidBinaryEncoding, BinaryDecodeFailure):
        message_type = "error._InvalidBinary"

        final_headers["_binaryEncoding"] = binary_encoder.encode_map

        return [message_type, final_headers, {}]

    except FunctionNotFound:
        message_type = "error._UnknownFunction"

        return [message_type, final_headers, {}]

    except ApplicationError as e:
        message_type = e.message_type

        return [message_type, final_headers, e.body]

    except Exception:
        message_type = "error._ApplicationFailure"

        return [message_type, final_headers, {}]


def validate_struct(namespace: str, reference_struct: Dict[str, FieldDeclaration], actual_struct: Dict[str, Any]) -> None:
    missing_fields = []
    for field_name, field_declaration in reference_struct.items():
        if field_name not in actual_struct and not field_declaration.optional:
            missing_fields.append(field_name)

    if missing_fields:
        raise StructMissingFields(namespace, missing_fields)

    extra_fields = []
    for name in actual_struct.keys():
        if name not in reference_struct:
            extra_fields.append(name)

    if extra_fields:
        raise StructHasExtraFields(namespace, extra_fields)

    for field_name, field in actual_struct.items():
        reference_field = reference_struct.get(field_name)
        if reference_field is None:
            raise StructHasExtraFields(namespace, [field_name])
        validate_type(f"{namespace}.{field_name}",
                      reference_field.type_declaration, field)


def validate_type(field_name: str, type_declaration: TypeDeclaration, value: Any) -> None:
    if value is None:
        if not type_declaration.nullable:
            raise InvalidFieldType(
                field_name, InvalidFieldTypeError.NULL_INVALID_FOR_NON_NULL_TYPE)
        else:
            return
    else:
        expected_type = type_declaration.type

        if isinstance(expected_type, JsonBoolean):
            if isinstance(value, bool):
                return
            elif isinstance(value, (int, float)):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.NUMBER_INVALID_FOR_BOOLEAN_TYPE)
            elif isinstance(value, str):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.STRING_INVALID_FOR_BOOLEAN_TYPE)
            elif isinstance(value, List):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.ARRAY_INVALID_FOR_BOOLEAN_TYPE)
            elif isinstance(value, Dict):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.OBJECT_INVALID_FOR_BOOLEAN_TYPE)
            else:
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.VALUE_INVALID_FOR_BOOLEAN_TYPE)

        elif isinstance(expected_type, JsonInteger):
            if isinstance(value, bool):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_INTEGER_TYPE)
            elif isinstance(value, (int, float)):
                if isinstance(value, (int)):
                    return
                else:
                    raise InvalidFieldType(
                        field_name, InvalidFieldTypeError.NUMBER_INVALID_FOR_INTEGER_TYPE)
            elif isinstance(value, str):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.STRING_INVALID_FOR_INTEGER_TYPE)
            elif isinstance(value, List):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.ARRAY_INVALID_FOR_INTEGER_TYPE)
            elif isinstance(value, Dict):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.OBJECT_INVALID_FOR_INTEGER_TYPE)
            else:
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.VALUE_INVALID_FOR_INTEGER_TYPE)

        elif isinstance(expected_type, JsonNumber):
            if isinstance(value, bool):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_NUMBER_TYPE)
            elif isinstance(value, (int, float)):
                return
            elif isinstance(value, str):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.STRING_INVALID_FOR_NUMBER_TYPE)
            elif isinstance(value, List):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.ARRAY_INVALID_FOR_NUMBER_TYPE)
            elif isinstance(value, Dict):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.OBJECT_INVALID_FOR_NUMBER_TYPE)
            else:
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.OBJECT_INVALID_FOR_NUMBER_TYPE)

        elif isinstance(expected_type, JsonString):
            if isinstance(value, bool):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_STRING_TYPE)
            elif isinstance(value, (int, float)):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.NUMBER_INVALID_FOR_STRING_TYPE)
            elif isinstance(value, str):
                return
            elif isinstance(value, List):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.ARRAY_INVALID_FOR_STRING_TYPE)
            elif isinstance(value, Dict):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.OBJECT_INVALID_FOR_STRING_TYPE)
            else:
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.VALUE_INVALID_FOR_STRING_TYPE)

        elif isinstance(expected_type, JsonArray):
            if isinstance(value, bool):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ARRAY_TYPE)
            elif isinstance(value, (int, float)):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.NUMBER_INVALID_FOR_ARRAY_TYPE)
            elif isinstance(value, str):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.STRING_INVALID_FOR_ARRAY_TYPE)
            elif isinstance(value, List):
                for i, element in enumerate(value):
                    validate_type(
                        f"{field_name}[{i}]", expected_type.nested_type, element)
                return
            elif isinstance(value, Dict):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.OBJECT_INVALID_FOR_ARRAY_TYPE)
            else:
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.VALUE_INVALID_FOR_ARRAY_TYPE)

        elif isinstance(expected_type, JsonObject):
            if isinstance(value, bool):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_OBJECT_TYPE)
            elif isinstance(value, (int, float)):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.NUMBER_INVALID_FOR_OBJECT_TYPE)
            elif isinstance(value, str):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.STRING_INVALID_FOR_OBJECT_TYPE)
            elif isinstance(value, List):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.ARRAY_INVALID_FOR_OBJECT_TYPE)
            elif isinstance(value, Dict):
                for k, v in value.items():
                    validate_type(f"{field_name}{{{k}}}",
                                  expected_type.nested_type, v)
                return
            else:
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.VALUE_INVALID_FOR_OBJECT_TYPE)

        elif isinstance(expected_type, Struct):
            if isinstance(value, bool):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_STRUCT_TYPE)
            elif isinstance(value, (int, float)):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.NUMBER_INVALID_FOR_STRUCT_TYPE)
            elif isinstance(value, str):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.STRING_INVALID_FOR_STRUCT_TYPE)
            elif isinstance(value, List):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.ARRAY_INVALID_FOR_STRUCT_TYPE)
            elif isinstance(value, Dict):
                validate_struct(field_name, expected_type.fields, value)
                return
            else:
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.VALUE_INVALID_FOR_STRUCT_TYPE)

        elif isinstance(expected_type, Enum):
            if isinstance(value, bool):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ENUM_TYPE)
            elif isinstance(value, (int, float)):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.NUMBER_INVALID_FOR_ENUM_TYPE)
            elif isinstance(value, str):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.STRING_INVALID_FOR_ENUM_TYPE)
            elif isinstance(value, List):
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.ARRAY_INVALID_FOR_ENUM_TYPE)
            elif isinstance(value, Dict):
                if len(value) != 1:
                    raise EnumDoesNotHaveOnlyOneField(field_name)

                enum_case, enum_value = next(iter(value.items()))

                if isinstance(enum_value, bool):
                    raise InvalidFieldType(
                        field_name, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ENUM_STRUCT_TYPE)
                elif isinstance(enum_value, (int, float)):
                    raise InvalidFieldType(
                        field_name, InvalidFieldTypeError.NUMBER_INVALID_FOR_ENUM_STRUCT_TYPE)
                elif isinstance(enum_value, str):
                    raise InvalidFieldType(
                        field_name, InvalidFieldTypeError.STRING_INVALID_FOR_ENUM_STRUCT_TYPE)
                elif isinstance(enum_value, List):
                    raise InvalidFieldType(
                        field_name, InvalidFieldTypeError.ARRAY_INVALID_FOR_ENUM_STRUCT_TYPE)
                elif isinstance(enum_value, Dict):
                    validate_enum(field_name, expected_type.cases(),
                                  enum_case, enum_value)
                    return
                else:
                    raise InvalidFieldType(
                        field_name, InvalidFieldTypeError.VALUE_INVALID_FOR_ENUM_STRUCT_TYPE)

            else:
                raise InvalidFieldType(
                    field_name, InvalidFieldTypeError.VALUE_INVALID_FOR_ENUM_TYPE)

        elif isinstance(expected_type, JsonAny):
            pass  # All values validate for any

        else:
            raise InvalidFieldType(
                field_name, InvalidFieldTypeError.INVALID_TYPE)


def validate_enum(namespace: str, reference: Dict[str, Dict[str, Any]], enum_case: str, actual: Dict[str, Any]) -> None:
    reference_field = reference.get(enum_case)
    if reference_field is None:
        raise UnknownEnumField(f"{namespace}.{enum_case}")

    validate_struct(f"{namespace}.{enum_case}",
                    reference_field["fields"], actual)


class UnknownEnumField(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


def create_invalid_field_full(e: InvalidFieldType) -> Tuple[str, Dict[str, List[Dict[str, str]]]]:
    entries = {
        InvalidFieldTypeError.NULL_INVALID_FOR_NON_NULL_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "null_invalid_for_non_null_type")
        ),
        InvalidFieldTypeError.NUMBER_INVALID_FOR_BOOLEAN_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "number_invalid_for_boolean_type")
        ),
        InvalidFieldTypeError.STRING_INVALID_FOR_BOOLEAN_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "string_invalid_for_boolean_type")
        ),
        InvalidFieldTypeError.ARRAY_INVALID_FOR_BOOLEAN_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "array_invalid_for_boolean_type")
        ),
        InvalidFieldTypeError.OBJECT_INVALID_FOR_BOOLEAN_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "object_invalid_for_boolean_type")
        ),
        InvalidFieldTypeError.VALUE_INVALID_FOR_BOOLEAN_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "value_invalid_for_boolean_type")
        ),
        InvalidFieldTypeError.BOOLEAN_INVALID_FOR_INTEGER_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "boolean_invalid_for_integer_type")
        ),
        InvalidFieldTypeError.NUMBER_INVALID_FOR_INTEGER_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "number_invalid_for_integer_type")
        ),
        InvalidFieldTypeError.STRING_INVALID_FOR_INTEGER_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "string_invalid_for_integer_type")
        ),
        InvalidFieldTypeError.ARRAY_INVALID_FOR_INTEGER_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "array_invalid_for_integer_type")
        ),
        InvalidFieldTypeError.OBJECT_INVALID_FOR_INTEGER_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "object_invalid_for_integer_type")
        ),
        InvalidFieldTypeError.VALUE_INVALID_FOR_INTEGER_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "value_invalid_for_integer_type")
        ),
        InvalidFieldTypeError.BOOLEAN_INVALID_FOR_NUMBER_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "boolean_invalid_for_number_type")
        ),
        InvalidFieldTypeError.STRING_INVALID_FOR_NUMBER_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "string_invalid_for_number_type")
        ),
        InvalidFieldTypeError.ARRAY_INVALID_FOR_NUMBER_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "array_invalid_for_number_type")
        ),
        InvalidFieldTypeError.OBJECT_INVALID_FOR_NUMBER_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "object_invalid_for_number_type")
        ),
        InvalidFieldTypeError.VALUE_INVALID_FOR_NUMBER_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "value_invalid_for_number_type")
        ),
        InvalidFieldTypeError.BOOLEAN_INVALID_FOR_STRING_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "boolean_invalid_for_string_type")
        ),
        InvalidFieldTypeError.NUMBER_INVALID_FOR_STRING_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "number_invalid_for_string_type")
        ),
        InvalidFieldTypeError.ARRAY_INVALID_FOR_STRING_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "array_invalid_for_string_type")
        ),
        InvalidFieldTypeError.OBJECT_INVALID_FOR_STRING_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "object_invalid_for_string_type")
        ),
        InvalidFieldTypeError.VALUE_INVALID_FOR_STRING_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "value_invalid_for_string_type")
        ),
        InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ARRAY_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "boolean_invalid_for_array_type")
        ),
        InvalidFieldTypeError.NUMBER_INVALID_FOR_ARRAY_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "number_invalid_for_array_type")
        ),
        InvalidFieldTypeError.STRING_INVALID_FOR_ARRAY_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "string_invalid_for_array_type")
        ),
        InvalidFieldTypeError.OBJECT_INVALID_FOR_ARRAY_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "object_invalid_for_array_type")
        ),
        InvalidFieldTypeError.VALUE_INVALID_FOR_ARRAY_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "value_invalid_for_array_type")
        ),
        InvalidFieldTypeError.BOOLEAN_INVALID_FOR_OBJECT_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "boolean_invalid_for_object_type")
        ),
        InvalidFieldTypeError.NUMBER_INVALID_FOR_OBJECT_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "number_invalid_for_object_type")
        ),
        InvalidFieldTypeError.STRING_INVALID_FOR_OBJECT_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "string_invalid_for_object_type")
        ),
        InvalidFieldTypeError.ARRAY_INVALID_FOR_OBJECT_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "array_invalid_for_object_type")
        ),
        InvalidFieldTypeError.VALUE_INVALID_FOR_OBJECT_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "value_invalid_for_object_type")
        ),
        InvalidFieldTypeError.BOOLEAN_INVALID_FOR_STRUCT_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "boolean_invalid_for_struct_type")
        ),
        InvalidFieldTypeError.NUMBER_INVALID_FOR_STRUCT_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "number_invalid_for_struct_type")
        ),
        InvalidFieldTypeError.STRING_INVALID_FOR_STRUCT_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "string_invalid_for_struct_type")
        ),
        InvalidFieldTypeError.ARRAY_INVALID_FOR_STRUCT_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "array_invalid_for_struct_type")
        ),
        InvalidFieldTypeError.VALUE_INVALID_FOR_STRUCT_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "value_invalid_for_struct_type")
        ),
        InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ENUM_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "boolean_invalid_for_enum_type")
        ),
        InvalidFieldTypeError.NUMBER_INVALID_FOR_ENUM_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "number_invalid_for_enum_type")
        ),
        InvalidFieldTypeError.STRING_INVALID_FOR_ENUM_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "string_invalid_for_enum_type")
        ),
        InvalidFieldTypeError.ARRAY_INVALID_FOR_ENUM_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "array_invalid_for_enum_type")
        ),
        InvalidFieldTypeError.VALUE_INVALID_FOR_ENUM_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "value_invalid_for_enum_type")
        ),
        InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ENUM_STRUCT_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "boolean_invalid_for_enum_struct_type")
        ),
        InvalidFieldTypeError.NUMBER_INVALID_FOR_ENUM_STRUCT_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "number_invalid_for_enum_struct_type")
        ),
        InvalidFieldTypeError.STRING_INVALID_FOR_ENUM_STRUCT_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "string_invalid_for_enum_struct_type")
        ),
        InvalidFieldTypeError.ARRAY_INVALID_FOR_ENUM_STRUCT_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "array_invalid_for_enum_struct_type")
        ),
        InvalidFieldTypeError.VALUE_INVALID_FOR_ENUM_STRUCT_TYPE: (
            "error._invalid_input",
            create_invalid_field(
                e.field_name, "value_invalid_for_enum_struct_type")
        ),
        InvalidFieldTypeError.INVALID_ENUM_VALUE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "unknown_enum_value")
        ),
        InvalidFieldTypeError.INVALID_TYPE: (
            "error._invalid_input",
            create_invalid_field(e.field_name, "invalid_type")
        ),
    }
    return entries.get(e.error)


def create_invalid_field(field: str, reason: str) -> Dict[str, List[Dict[str, str]]]:
    return create_invalid_fields({field: reason})


def create_invalid_fields(errors: Dict[str, str]) -> Dict[str, List[Dict[str, str]]]:
    json_errors = [
        {"field": key, "reason": value}
        for key, value in errors.items()
    ]
    return {"cases": json_errors}


def slice_types(type_: Any, value: Any, sliced_types: Dict[str, List[str]]) -> Any:
    if isinstance(type_, Struct):
        sliced_fields = sliced_types.get(type_.name)
        value_as_map = value
        final_map = {}
        for key, entry in value_as_map.items():
            if sliced_fields is None or key in sliced_fields:
                field = type_.fields.get(key)
                sliced_value = slice_types(
                    field.type_declaration.type_, entry, sliced_types)
                final_map[key] = sliced_value
        return final_map
    elif isinstance(type_, Enum):
        value_as_map = value
        enum_entry = next(iter(value_as_map.items()))
        struct_reference = type_.cases.get(enum_entry[0])
        new_struct = {}
        for key, struct_entry in struct_reference.fields.items():
            sliced_value = slice_types(
                struct_entry.value.type_declaration.type_, enum_entry[1], sliced_types)
            new_struct[key] = sliced_value
        return {enum_entry[0]: new_struct}
    elif isinstance(type_, JsonObject):
        value_as_map = value
        final_map = {}
        for key, entry in value_as_map.items():
            sliced_value = slice_types(
                type_.nested_type.type_, entry, sliced_types)
            final_map[key] = sliced_value
        return final_map
    elif isinstance(type_, JsonArray):
        value_as_list = value
        final_list = []
        for entry in value_as_list:
            sliced_value = slice_types(
                type_.nested_type.type_, entry, sliced_types)
            final_list.append(sliced_value)
        return final_list
    else:
        return value
