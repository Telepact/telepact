from typing import Any, Dict, List, Optional, Union


class Type:
    def get_name(self) -> str:
        raise NotImplementedError


class Definition:
    def get_name(self) -> str:
        raise NotImplementedError


class Japi:
    def __init__(self, original: Dict[str, Any], parsed: Dict[str, Definition]) -> None:
        self.original = original
        self.parsed = parsed


class JsonAny(Type):
    def get_name(self) -> str:
        return "any"


class JsonArray(Type):
    def __init__(self, nested_type: TypeDeclaration) -> None:
        self.nested_type = nested_type

    def get_name(self) -> str:
        return "array"


class JsonBoolean(Type):
    def get_name(self) -> str:
        return "boolean"


class JsonInteger(Type):
    def get_name(self) -> str:
        return "integer"


class JsonNull(Type):
    def get_name(self) -> str:
        return "null"


class JsonNumber(Type):
    def get_name(self) -> str:
        return "number"


class JsonObject(Type):
    def __init__(self, nested_type: TypeDeclaration) -> None:
        self.nested_type = nested_type

    def get_name(self) -> str:
        return "object"


class JsonString(Type):
    def get_name(self) -> str:
        return "string"


class Struct(Type):
    def __init__(self, name: str, fields: Dict[str, FieldDeclaration]) -> None:
        self.name = name
        self.fields = fields

    def get_name(self) -> str:
        return self.name


class Enum(Type):
    def __init__(self, name: str, cases: Dict[str, Struct]) -> None:
        self.name = name
        self.cases = cases

    def get_name(self) -> str:
        return self.name


class ErrorDefinition(Definition):
    def __init__(self, name: str, fields: Dict[str, FieldDeclaration]) -> None:
        self.name = name
        self.fields = fields

    def get_name(self) -> str:
        return self.name


class FunctionDefinition(Definition):
    def __init__(self, name: str, input_struct: Struct, output_struct: Struct, errors: List[str]) -> None:
        self.name = name
        self.input_struct = input_struct
        self.output_struct = output_struct
        self.errors = errors

    def get_name(self) -> str:
        return self.name


class FieldDeclaration:
    def __init__(self, type_declaration: TypeDeclaration, optional: bool) -> None:
        self.type_declaration = type_declaration
        self.optional = optional


class FieldNameAndFieldDeclaration:
    def __init__(self, field_name: str, field_declaration: FieldDeclaration) -> None:
        self.field_name = field_name
        self.field_declaration = field_declaration


class TitleDefinition(Definition):
    def __init__(self, name: str) -> None:
        self.name = name

    def get_name(self) -> str:
        return self.name


class TypeDefinition(Definition):
    def __init__(self, name: str, type: Type) -> None:
        self.name = name
        self.type = type

    def get_name(self) -> str:
        return self.name


class TypeDeclaration:
    def __init__(self, type: Type, nullable: bool) -> None:
        self.type = type
        self.nullable = nullable


class JapiMessageArrayTooFewElements(RuntimeError):
    pass


class JapiMessageTypeNotString(RuntimeError):
    pass


class JapiMessageNotArray(RuntimeError):
    pass


class JapiMessageTypeNotFunction(RuntimeError):
    pass


class JapiMessageHeaderNotObject(RuntimeError):
    pass


class InvalidBinaryEncoding(RuntimeError):
    pass


class InvalidSelectFieldsHeader(RuntimeError):
    pass


class BinaryDecodeFailure(RuntimeError):
    def __init__(self, cause: Exception) -> None:
        super().__init__(cause)


class JapiMessageBodyNotObject(RuntimeError):
    pass


class FunctionNotFound(RuntimeError):
    def __init__(self, function_name: str) -> None:
        super().__init__("Function not found: %s" % function_name)
        self.function_name = function_name


class InvalidInput(RuntimeError):
    def __init__(self, cause: Optional[Exception] = None) -> None:
        super().__init__(cause)


class InvalidOutput(RuntimeError):
    def __init__(self, cause: Exception) -> None:
        super().__init__(cause)


class InvalidApplicationFailure(RuntimeError):
    def __init__(self, cause: Exception) -> None:
        super().__init__(cause)


class DisallowedError(RuntimeError):
    def __init__(self, cause: Exception) -> None:
        super().__init__(cause)


class FieldError(InvalidInput):
    pass


class StructMissingFields(FieldError):
    def __init__(self, namespace: str, missing_fields: List[str]) -> None:
        super().__init__()
        self.namespace = namespace
        self.missing_fields = missing_fields


class StructHasExtraFields(FieldError):
    def __init__(self, namespace: str, extra_fields: List[str]) -> None:
        super().__init__()
        self.namespace = namespace
        self.extra_fields = extra_fields


class EnumDoesNotHaveOnlyOneField(FieldError):
    def __init__(self, namespace: str) -> None:
        super().__init__()
        self.namespace = namespace


class UnknownEnumField(FieldError):
    def __init__(self, namespace: str, field: str) -> None:
        super().__init__()
        self.namespace = namespace
        self.field = field


class InvalidFieldType(FieldError):
    def __init__(self, field_name: str, error: InvalidFieldTypeError, cause: Optional[Exception] = None) -> None:
        super().__init__(cause)
        self.field_name = field_name
        self.error = error


class IncorrectBinaryHashException(Exception):
    pass


class InvalidFieldTypeError(Enum):
    NULL_INVALID_FOR_NON_NULL_TYPE = 1

    NUMBER_INVALID_FOR_BOOLEAN_TYPE = 2
    STRING_INVALID_FOR_BOOLEAN_TYPE = 3
    ARRAY_INVALID_FOR_BOOLEAN_TYPE = 4
    OBJECT_INVALID_FOR_BOOLEAN_TYPE = 5
    VALUE_INVALID_FOR_BOOLEAN_TYPE = 6

    BOOLEAN_INVALID_FOR_INTEGER_TYPE = 7
    NUMBER_INVALID_FOR_INTEGER_TYPE = 8
    STRING_INVALID_FOR_INTEGER_TYPE = 9
    ARRAY_INVALID_FOR_INTEGER_TYPE = 10
    OBJECT_INVALID_FOR_INTEGER_TYPE = 11
    VALUE_INVALID_FOR_INTEGER_TYPE = 12

    BOOLEAN_INVALID_FOR_NUMBER_TYPE = 13
    STRING_INVALID_FOR_NUMBER_TYPE = 14
    ARRAY_INVALID_FOR_NUMBER_TYPE = 15
    OBJECT_INVALID_FOR_NUMBER_TYPE = 16
    VALUE_INVALID_FOR_NUMBER_TYPE = 17

    BOOLEAN_INVALID_FOR_STRING_TYPE = 18
    NUMBER_INVALID_FOR_STRING_TYPE = 19
    ARRAY_INVALID_FOR_STRING_TYPE = 20
    OBJECT_INVALID_FOR_STRING_TYPE = 21
    VALUE_INVALID_FOR_STRING_TYPE = 22

    BOOLEAN_INVALID_FOR_ARRAY_TYPE = 23
    NUMBER_INVALID_FOR_ARRAY_TYPE = 24
    STRING_INVALID_FOR_ARRAY_TYPE = 25
    OBJECT_INVALID_FOR_ARRAY_TYPE = 26
    VALUE_INVALID_FOR_ARRAY_TYPE = 27

    BOOLEAN_INVALID_FOR_OBJECT_TYPE = 28
    NUMBER_INVALID_FOR_OBJECT_TYPE = 29
    STRING_INVALID_FOR_OBJECT_TYPE = 30
    ARRAY_INVALID_FOR_OBJECT_TYPE = 31
    VALUE_INVALID_FOR_OBJECT_TYPE = 32

    BOOLEAN_INVALID_FOR_STRUCT_TYPE = 33
    NUMBER_INVALID_FOR_STRUCT_TYPE = 34
    STRING_INVALID_FOR_STRUCT_TYPE = 35
    ARRAY_INVALID_FOR_STRUCT_TYPE = 36
    VALUE_INVALID_FOR_STRUCT_TYPE = 37

    BOOLEAN_INVALID_FOR_ENUM_TYPE = 38
    NUMBER_INVALID_FOR_ENUM_TYPE = 39
    STRING_INVALID_FOR_ENUM_TYPE = 40
    ARRAY_INVALID_FOR_ENUM_TYPE = 41
    VALUE_INVALID_FOR_ENUM_TYPE = 42

    BOOLEAN_INVALID_FOR_ENUM_STRUCT_TYPE = 43
    NUMBER_INVALID_FOR_ENUM_STRUCT_TYPE = 44
    STRING_INVALID_FOR_ENUM_STRUCT_TYPE = 45
    ARRAY_INVALID_FOR_ENUM_STRUCT_TYPE = 46
    VALUE_INVALID_FOR_ENUM_STRUCT_TYPE = 47

    INVALID_ENUM_VALUE = 48
    INVALID_TYPE = 49
