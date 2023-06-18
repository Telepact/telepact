import json
from typing import List, Dict, Any, Union, cast
import re


class Type:
    def get_name(self) -> str:
        raise NotImplementedError


class JsonNull(Type):
    def get_name(self) -> str:
        return "null"


class JsonBoolean(Type):
    def get_name(self) -> str:
        return "boolean"


class JsonInteger(Type):
    def get_name(self) -> str:
        return "integer"


class JsonNumber(Type):
    def get_name(self) -> str:
        return "number"


class JsonString(Type):
    def get_name(self) -> str:
        return "string"


class JsonArray(Type):
    def __init__(self, nested_type: 'TypeDeclaration'):
        self.nested_type = nested_type

    def get_name(self) -> str:
        return "array"


class JsonObject(Type):
    def __init__(self, nested_type: 'TypeDeclaration'):
        self.nested_type = nested_type

    def get_name(self) -> str:
        return "object"


class Struct(Type):
    def __init__(self, name: str, fields: Dict[str, 'FieldDeclaration']):
        self.name = name
        self.fields = fields

    def get_name(self) -> str:
        return self.name


class Enum(Type):
    def __init__(self, name: str, cases: Dict[str, 'Struct']):
        self.name = name
        self.cases = cases

    def get_name(self) -> str:
        return self.name


class JsonAny(Type):
    def get_name(self) -> str:
        return "any"


class TypeDeclaration:
    def __init__(self, type: Type, nullable: bool):
        self.type = type
        self.nullable = nullable


class Definition:
    def get_name(self) -> str:
        raise NotImplementedError


class FieldDeclaration:
    def __init__(self, type_declaration: TypeDeclaration, optional: bool):
        self.type_declaration = type_declaration
        self.optional = optional


class FunctionDefinition(Definition):
    def __init__(self, name: str, input_struct: Struct, output_struct: Struct, errors: List[str]):
        self.name = name
        self.input_struct = input_struct
        self.output_struct = output_struct
        self.errors = errors

    def get_name(self) -> str:
        return self.name


class TypeDefinition(Definition):
    def __init__(self, name: str, type: Type):
        self.name = name
        self.type = type

    def get_name(self) -> str:
        return self.name


class ErrorDefinition(Definition):
    def __init__(self, name: str, fields: Dict[str, FieldDeclaration]):
        self.name = name
        self.fields = fields

    def get_name(self) -> str:
        return self.name


class TitleDefinition(Definition):
    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        return self.name


class FieldNameAndFieldDeclaration:
    def __init__(self, field_name: str, field_declaration: FieldDeclaration):
        self.field_name = field_name
        self.field_declaration = field_declaration


class JapiParseError(RuntimeError):
    def __init__(self, message: str):
        super().__init__(message)


class Japi:
    def __init__(self, original: Dict[str, object], parsed: Dict[str, Definition]):
        self.original = original
        self.parsed = parsed


def parse_type(japi_as_json_java: Dict[str, List[object]], parsed_definitions: Dict[str, Definition], type_declaration: str) -> TypeDeclaration:
    regex = re.compile(
        r"^((null|boolean|integer|number|string|any)|((array|object)(<(.*)>)?)|((enum|struct)\.([a-zA-Z_]\w*)))(\?)?$")
    matcher = regex.match(type_declaration)

    nullable = matcher.group(10) is not None

    try:
        name = matcher.group(2)
        if name is None:
            raise RuntimeError("Ignore: will try another type")

        type_ = {
            "null": JsonNull(),
            "boolean": JsonBoolean(),
            "integer": JsonInteger(),
            "number": JsonNumber(),
            "string": JsonString(),
            "any": JsonAny()
        }.get(name)

        if type_ is None:
            raise JapiParseError("Unrecognized type: {}".format(name))

        if isinstance(type_, JsonNull):
            if nullable:
                raise JapiParseError("Cannot declare null type as nullable")
            nullable = True

        return TypeDeclaration(type_, nullable)
    except (Exception, JapiParseError) as e:
        if isinstance(e, JapiParseError):
            raise e

    try:
        name = matcher.group(4)
        if name is None:
            raise RuntimeError("Ignore: will try another type")

        nested_name = matcher.group(6)

        nested_type = parse_type(japi_as_json_java, parsed_definitions,
                                 nested_name) if nested_name else TypeDeclaration(JsonAny(), False)

        type_ = {
            "array": JsonArray(nested_type),
            "object": JsonObject(nested_type)
        }.get(name)

        if type_ is None:
            raise JapiParseError("Unrecognized type: {}".format(name))

        return TypeDeclaration(type_, nullable)
    except (Exception, JapiParseError) as e:
        if isinstance(e, JapiParseError):
            raise e

    try:
        name = matcher.group(7)
        if name is None:
            raise RuntimeError("Ignore: will try another type")

        definition = parsed_definitions.setdefault(name, parse_definition(
            japi_as_json_java, parsed_definitions, type_declaration))
        if isinstance(definition, TypeDefinition):
            return TypeDeclaration(definition.type, nullable)
        elif isinstance(definition, FunctionDefinition):
            raise JapiParseError(
                "Cannot reference a function in type declarations")
        elif isinstance(definition, ErrorDefinition):
            raise JapiParseError(
                "Cannot reference an error in type declarations")
    except (Exception, JapiParseError) as e:
        if isinstance(e, JapiParseError):
            raise e

    raise JapiParseError(
        "Invalid type declaration: {}".format(type_declaration))


def parse_field(
    japi_as_json_java: Dict[str, List[object]],
    parsed_definitions: Dict[str, 'Definition'],
    field_declaration: str,
    type_declaration_value: object,
    is_for_union: bool
) -> FieldNameAndFieldDeclaration:
    regex = re.compile(r"^([a-zA-Z_]+[a-zA-Z0-9_]*)(!)?$")
    matcher = regex.match(field_declaration)

    field_name = matcher.group(1)

    optional = matcher.group(2) is not None

    if optional and is_for_union:
        raise JapiParseError("Union keys cannot be marked as optional")

    try:
        type_declaration_string = str(type_declaration_value)
    except TypeError:
        raise JapiParseError("Type declarations should be strings")

    type_declaration = parse_type(
        japi_as_json_java, parsed_definitions, type_declaration_string)

    return FieldNameAndFieldDeclaration(field_name, FieldDeclaration(type_declaration, optional))


def split_definition_keyword_and_name(name: str) -> List[str]:
    regex = re.compile(
        r"^(struct|union|enum|error|function|event|info).([a-zA-Z_]+[a-zA-Z0-9_]*)$")
    matcher = regex.match(name)

    keyword = matcher.group(1)
    part_name = matcher.group(2)

    return [keyword, part_name]


def parse_definition(
    japi_as_json_java: Dict[str, List[object]],
    parsed_definitions: Dict[str, Definition],
    definition_key: str
) -> Definition:
    definition_as_json_java_with_doc = japi_as_json_java.get(definition_key)
    if definition_as_json_java_with_doc is None:
        raise JapiParseError(
            "Could not find definition for {}".format(definition_key))

    split_name = split_definition_keyword_and_name(definition_key)
    keyword = split_name[0]
    definition_name = split_name[1]

    definition_as_json_java = definition_as_json_java_with_doc[1]

    parsed_definition = None

    if keyword == "function":
        try:
            definition_array = cast(List[Any], definition_as_json_java)
            input_definition_as_json_java = cast(
                Dict[str, Any], definition_array[0])
        except (IndexError, TypeError):
            raise JapiParseError(
                "Invalid function definition for {}".format(definition_key))

        input_fields = {}
        for field_declaration, type_declaration_value in input_definition_as_json_java.items():
            parsed_field = parse_field(
                japi_as_json_java, parsed_definitions, field_declaration, type_declaration_value, False)
            input_fields[parsed_field.field_name] = parsed_field.field_declaration

        try:
            output_definition_as_json_java = cast(
                Dict[str, Any], definition_array[2])
        except (IndexError, TypeError):
            raise JapiParseError(
                "Invalid function definition for {}".format(definition_key))

        output_fields = {}
        for field_declaration, type_declaration_value in output_definition_as_json_java.items():
            parsed_field = parse_field(
                japi_as_json_java, parsed_definitions, field_declaration, type_declaration_value, False)
            output_fields[parsed_field.field_name] = parsed_field.field_declaration

        errors = []
        if len(definition_array) == 4:
            error_definition = definition_array[3]

            try:
                errors = cast(List[str], error_definition)
            except TypeError:
                raise JapiParseError(
                    "Invalid function definition for {}".format(definition_key))

            for error_def in errors:
                if error_def not in japi_as_json_java:
                    raise JapiParseError(
                        "Unknown error reference for {}".format(error_def))

        input_struct = Struct("{}_input".format(definition_key), input_fields)
        output_struct = Struct("{}_output".format(
            definition_key), output_fields)

        parsed_definition = FunctionDefinition(
            definition_key, input_struct, output_struct, errors)

    elif keyword == "struct":
        try:
            struct_definition_as_json_java = cast(
                Dict[str, Any], definition_as_json_java)
        except TypeError:
            raise JapiParseError(
                "Invalid struct definition for {}".format(definition_key))

        fields = {}
        for field_declaration, type_declaration_value in struct_definition_as_json_java.items():
            parsed_field = parse_field(
                japi_as_json_java, parsed_definitions, field_declaration, type_declaration_value, False)
            fields[parsed_field.field_name] = parsed_field.field_declaration

        type_obj = Struct(definition_key, fields)
        parsed_definition = TypeDefinition(definition_key, type_obj)

    elif keyword == "error":
        try:
            error_definition_as_json_java = cast(
                Dict[str, Any], definition_as_json_java)
        except TypeError:
            raise JapiParseError(
                "Invalid error definition for {}".format(definition_key))

        fields = {}
        for field_declaration, type_declaration_value in error_definition_as_json_java.items():
            parsed_field = parse_field(
                japi_as_json_java, parsed_definitions, field_declaration, type_declaration_value, False)
            fields[parsed_field.field_name] = parsed_field.field_declaration

        parsed_definition = ErrorDefinition(definition_key, fields)

    elif keyword == "enum":
        try:
            enum_definition_as_json_java = cast(
                Dict[str, Any], definition_as_json_java)
        except TypeError:
            raise JapiParseError(
                "Invalid enum definition for {}".format(definition_key))

        cases = {}
        for enum_case, case_struct_definition_as_java in enum_definition_as_json_java.items():
            try:
                case_struct_definition_as_java = cast(
                    Dict[str, Any], case_struct_definition_as_java)
            except TypeError:
                raise JapiParseError(
                    "Invalid enum definition for {}".format(definition_key))

            fields = {}
            for case_struct_field_declaration, case_struct_type_declaration_value in case_struct_definition_as_java.items():
                parsed_field = parse_field(japi_as_json_java, parsed_definitions,
                                           case_struct_field_declaration, case_struct_type_declaration_value, False)
                fields[parsed_field.field_name] = parsed_field.field_declaration

            struct = Struct("{}_{}".format(definition_key, enum_case), fields)
            cases[enum_case] = struct

        type_obj = Enum(definition_key, cases)
        parsed_definition = TypeDefinition(definition_key, type_obj)

    elif keyword == "info":
        parsed_definition = TitleDefinition(definition_key)

    else:
        raise JapiParseError("Unrecognized japi keyword {}".format(keyword))

    return parsed_definition


def split_definition_keyword_and_name(name: str) -> List[str]:
    regex = re.compile(
        r"^(struct|union|enum|error|function|event|info).([a-zA-Z_]+[a-zA-Z0-9_]*)$")
    matcher = regex.match(name)

    keyword = matcher.group(1)
    part_name = matcher.group(2)

    return [keyword, part_name]


def new_japi(japi_as_json: str) -> Japi:
    parsed_definitions = {}

    try:
        japi_as_json_java = json.loads(japi_as_json)

        for definition_key in japi_as_json_java:
            if definition_key not in parsed_definitions:
                definition = parse_definition(
                    japi_as_json_java, parsed_definitions, definition_key)
                parsed_definitions[definition_key] = definition
    except json.JSONDecodeError:
        raise JapiParseError("Document root must be an object")

    return Japi(japi_as_json_java, parsed_definitions)
