from typing import Any
import json


class Type:
    def __init__(self) -> None:
        pass

    def getName(self):
        pass


class JsonNull(Type):
    def __init__(self) -> None:
        super().__init__()

    def getName(self):
        return "null"


class JsonBoolean(Type):
    def __init__(self) -> None:
        super().__init__()

    def getName(self):
        return "boolean"


class JsonInteger(Type):
    def __init__(self) -> None:
        super().__init__()

    def getName(self):
        return "integer"


class JsonNumber(Type):
    def __init__(self) -> None:
        super().__init__()

    def getName(self):
        return "string"


class TypeDeclaration:
    def __init__(self, t: Type, nullable: bool) -> None:
        self.type = t
        self.nullable = nullable


class JsonArray(Type):
    def __init__(self, nested_type: TypeDeclaration) -> None:
        super().__init__()
        self.nested_type = nested_type

    def getName(self):
        return "array"


class JsonObject(Type):
    def __init__(self, nested_type: TypeDeclaration) -> None:
        super().__init__()
        self.nested_type = nested_type

    def getName(self):
        return "object"


class FieldDeclaration:
    def __init__(self, type_declaration: TypeDeclaration, optional: bool) -> None:
        self.type_declaration = type_declaration
        self.optional = optional


class Struct(Type):
    def __init__(self, name: str, fields: dict[str, FieldDeclaration]) -> None:
        super().__init__()
        self.name = name
        self.fields = fields

    def getName(self):
        return self.name


class Enum(Type):
    def __init__(self, name: str, fields: dict[str, Struct]) -> None:
        super().__init__()
        self.name = name
        self.fields = fields


class JsonAny(Type):
    def __init__(self) -> None:
        super().__init__()

    def getName(self):
        return "any"


class Definition:
    def __init__(self) -> None:
        pass

    def getName(self):
        pass


class FunctionDefinition(Definition):
    def __init__(self, name: str, input_struc: Struct, outputStruct: Struct, allowed_errors: list[str]) -> None:
        super().__init__()
        self.name = name
        self.input_struct = input_struc
        self.allowed_errors = allowed_errors

    def getName(self):
        return self.name


class TypeDefinition(Definition):
    def __init__(self, name: str, t: Type) -> None:
        super().__init__()
        self.name = name
        self.type = t

    def getName(self):
        return self.name


class ErrorDefinition(Definition):
    def __init__(self, name: str, fields: dict) -> None:
        super().__init__()
        self.name = name
        self.fields = fields

    def getName(self):
        return self.name


class TitleDefinition(Definition):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def getName(self):
        return self.name


class JapiParseError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class Japi():
    def __init__(self, original: dict[str, Any], parsed: dict[str, Definition]) -> None:
        pass


def newJapi(japi_as_json: str) -> Japi:
    parsed_definitions = dict[str, Definition]

    japi_as_json_python = json.loads(japi_as_json)

    for definition_key, _ in japi_as_json_python:
        if definition_key not in parsed_definitions:
            definition = _parse_definition(japi_as_json_python)


def _parse_definition(japi_as_json_python: dict[str, Any], parsed_definitions: dict[str, Definition], definition_key: str):
    definition_as_json_python = japi_as_json_python[definition_key]
    if not definition_as_json_python:
        raise JapiParseError(
            'could not find definition for {}'.format(definition_key))

    # todo
    pass
