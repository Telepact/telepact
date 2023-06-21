import json
from typing import Dict
from typing import List, Dict, Union
import re
from typing import List, Dict, Any, Union

from japi.internal_types import Definition, Enum, ErrorDefinition, FieldDeclaration, FieldNameAndFieldDeclaration, FunctionDefinition, Japi, JsonAny, JsonArray, JsonBoolean, JsonInteger, JsonNull, JsonNumber, JsonObject, JsonString, Struct, TitleDefinition, TypeDeclaration, TypeDefinition
from japi.japi_parse_error import JapiParseError


def new_japi(japi_as_json: str) -> Japi:
    parsed_definitions: Dict[str, Definition] = {}

    japi_as_json_python: Dict[str, Any] = json.loads(japi_as_json)

    for definition_key, definition_value in japi_as_json_python.items():
        if definition_key not in parsed_definitions:
            definition = parse_definition(
                japi_as_json_python, parsed_definitions, definition_key)
            parsed_definitions[definition_key] = definition

    return Japi(japi_as_json_python, parsed_definitions)


def parse_definition(
    japi_as_json_java: Dict[str, List[object]],
    parsed_definitions: Dict[str, Definition],
    definition_key: str
) -> Definition:
    definition_as_json_java_with_doc = japi_as_json_java.get(definition_key)
    if definition_as_json_java_with_doc is None:
        raise JapiParseError(f"Could not find definition for {definition_key}")

    regex = re.compile(
        "^(struct|union|enum|error|function|event|info).([a-zA-Z_]+[a-zA-Z0-9_]*)$")
    matcher = regex.match(definition_key)
    keyword = matcher.group(1)
    definition_name = matcher.group(2)

    definition_as_json_java = definition_as_json_java_with_doc[1]

    if keyword == "function":
        try:
            definition_array = definition_as_json_java
            input_definition_as_json_java = definition_array[0]
        except (IndexError, TypeError):
            raise JapiParseError(
                f"Invalid function definition for {definition_key}")

        input_fields: Dict[str, FieldDeclaration] = {}
        for field_declaration, type_declaration_value in input_definition_as_json_java.items():
            parsed_field = parse_field(
                japi_as_json_java, parsed_definitions, field_declaration, type_declaration_value, False)
            input_fields[parsed_field.field_name] = parsed_field.field_declaration

        try:
            output_definition_as_json_java = definition_array[2]
        except (IndexError, TypeError):
            raise JapiParseError(
                f"Invalid function definition for {definition_key}")

        output_fields: Dict[str, FieldDeclaration] = {}
        for field_declaration, type_declaration_value in output_definition_as_json_java.items():
            parsed_field = parse_field(
                japi_as_json_java, parsed_definitions, field_declaration, type_declaration_value, False)
            output_fields[parsed_field.field_name] = parsed_field.field_declaration

        errors: List[str] = []
        if len(definition_array) == 4:
            error_definition = definition_array[3]

            try:
                errors = list(error_definition)
            except TypeError:
                raise JapiParseError(
                    f"Invalid function definition for {definition_key}")

            for error_def in errors:
                if error_def not in japi_as_json_java:
                    raise JapiParseError(
                        f"Unknown error reference for {error_def}")

        input_struct = Struct(f"{definition_key}.input", input_fields)
        output_struct = Struct(f"{definition_key}.output", output_fields)

        return FunctionDefinition(definition_key, input_struct, output_struct, errors)

    elif keyword == "struct":
        try:
            struct_definition_as_json_java = definition_as_json_java
        except TypeError:
            raise JapiParseError(
                f"Invalid struct definition for {definition_key}")

        fields: Dict[str, FieldDeclaration] = {}
        for field_declaration, type_declaration_value in struct_definition_as_json_java.items():
            parsed_field = parse_field(
                japi_as_json_java, parsed_definitions, field_declaration, type_declaration_value, False)
            fields[parsed_field.field_name] = parsed_field.field_declaration

        type_ = Struct(definition_key, fields)

        return TypeDefinition(definition_key, type_)

    elif keyword == "error":
        try:
            error_definition_as_json_java = definition_as_json_java
        except TypeError:
            raise JapiParseError(
                f"Invalid error definition for {definition_key}")

        fields: Dict[str, FieldDeclaration] = {}
        for field_declaration, type_declaration_value in error_definition_as_json_java.items():
            parsed_field = parse_field(
                japi_as_json_java, parsed_definitions, field_declaration, type_declaration_value, False)
            fields[parsed_field.field_name] = parsed_field.field_declaration

        return ErrorDefinition(definition_key, fields)

    elif keyword == "enum":
        try:
            enum_definition_as_json_java = definition_as_json_java
        except TypeError:
            raise JapiParseError(
                f"Invalid enum definition for {definition_key}")

        cases: Dict[str, Struct] = {}
        for enum_case, case_struct_definition_as_java in enum_definition_as_json_java.items():
            try:
                case_struct_definition_as_java = dict(
                    case_struct_definition_as_java)
            except TypeError:
                raise JapiParseError(
                    f"Invalid enum definition for {definition_key}")

            fields: Dict[str, FieldDeclaration] = {}
            for case_struct_field_declaration, case_struct_type_declaration_value in case_struct_definition_as_java.items():
                case_struct_parsed_field = parse_field(
                    japi_as_json_java, parsed_definitions, case_struct_field_declaration, case_struct_type_declaration_value, False)
                fields[case_struct_parsed_field.field_name] = case_struct_parsed_field.field_declaration

            struct = Struct(f"{definition_key}.{enum_case}", fields)
            cases[enum_case] = struct

        type_ = Enum(definition_key, cases)

        return TypeDefinition(definition_key, type_)

    elif keyword == "info":
        return TitleDefinition(definition_key)

    else:
        raise JapiParseError(f"Unrecognized japi keyword {keyword}")


def parse_field(japi_as_json_java: Dict[str, List[Any]], parsed_definitions: Dict[str, Any], field_declaration: str, type_declaration_value: Any, is_for_union: bool) -> FieldNameAndFieldDeclaration:
    regex = re.compile(r"^([a-zA-Z_]+[a-zA-Z0-9_]*)(!)?$")
    matcher = regex.match(field_declaration)

    if not matcher:
        raise JapiParseError("Invalid field declaration: %s" %
                             field_declaration)

    field_name = matcher.group(1)
    optional = bool(matcher.group(2))

    if optional and is_for_union:
        raise JapiParseError("Union keys cannot be marked as optional")

    try:
        type_declaration_string = str(type_declaration_value)
    except TypeError:
        raise JapiParseError("Type declarations should be strings")

    type_declaration = parse_type(
        japi_as_json_java, parsed_definitions, type_declaration_string)

    return FieldNameAndFieldDeclaration(field_name, FieldDeclaration(type_declaration, optional))


def parse_type(japi_as_json_java: Dict[str, List[Any]], parsed_definitions: Dict[str, Any], type_declaration: str) -> TypeDeclaration:
    regex = re.compile(
        r"^((null|boolean|integer|number|string|any)|((array|object)(<(.*)>)?)|((enum|struct)\.([a-zA-Z_]\w*)))(\?)?$")
    matcher = regex.match(type_declaration)

    if not matcher:
        raise JapiParseError("Invalid type declaration: %s" % type_declaration)

    nullable = bool(matcher.group(10))

    try:
        name = matcher.group(2)
        if name is None:
            raise RuntimeError("Ignore: will try another type")

        if name == "null":
            if nullable:
                raise JapiParseError("Cannot declare null type as nullable")
            nullable = True
            return TypeDeclaration(JsonNull(), nullable)

        type_obj = None
        if name == "boolean":
            type_obj = JsonBoolean()
        elif name == "integer":
            type_obj = JsonInteger()
        elif name == "number":
            type_obj = JsonNumber()
        elif name == "string":
            type_obj = JsonString()
        elif name == "any":
            type_obj = JsonAny()
        else:
            raise JapiParseError("Unrecognized type: %s" % name)

        return TypeDeclaration(type_obj, nullable)
    except JapiParseError as e1:
        raise e1
    except Exception:
        pass

    try:
        name = matcher.group(4)
        if name is None:
            raise RuntimeError("Ignore: will try another type")

        nested_name = matcher.group(6)
        nested_type = None
        if nested_name:
            nested_type = parse_type(
                japi_as_json_java, parsed_definitions, nested_name)
        else:
            nested_type = TypeDeclaration(JsonAny(), False)

        type_obj = None
        if name == "array":
            type_obj = JsonArray(nested_type)
        elif name == "object":
            type_obj = JsonObject(nested_type)
        else:
            raise JapiParseError("Unrecognized type: %s" % name)

        return TypeDeclaration(type_obj, nullable)
    except JapiParseError as e1:
        raise e1
    except Exception:
        pass

    name = matcher.group(7)
    if name is None:
        raise RuntimeError("Ignore: will try another type")

    definition = parsed_definitions.setdefault(name, parse_definition(
        japi_as_json_java, parsed_definitions, name))
    if isinstance(definition, TypeDefinition):
        return TypeDeclaration(definition.type, nullable)
    elif isinstance(definition, FunctionDefinition):
        raise JapiParseError(
            "Cannot reference a function in type declarations")
    elif isinstance(definition, ErrorDefinition):
        raise JapiParseError(
            "Cannot reference an error in type declarations")
    else:
        raise JapiParseError("Unknown definition: %s" % type_declaration)
