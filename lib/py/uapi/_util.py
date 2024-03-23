import binascii
from concurrent.futures import Future
from typing import Any, Coroutine, Dict, List, Tuple, Callable, Union, Callable, List, Union, Dict, Any, Tuple,  Optional, Set, Pattern, cast
from collections import OrderedDict, defaultdict
from hashlib import sha256
import json
import uapi
import uapi._random_generator as _rg
import uapi._util_types as _types
import uapi.types as types
import re
from msgpack import ExtType
import importlib.resources
import asyncio
import sys

_ANY_NAME = "Any"
_ARRAY_NAME = "Array"
_BOOLEAN_NAME = "Boolean"
_FN_NAME = "Object"
_INTEGER_NAME = "Integer"
_MOCK_CALL_NAME = "_ext._Call"
_MOCK_STUB_NAME = "_ext._Stub"
_NUMBER_NAME = "Number"
_OBJECT_NAME = "Object"
_STRING_NAME = "String"
_STRUCT_NAME = "Object"
_UNION_NAME = "Object"
_SELECT_NAME = "Object"


def get_internal_uapi_json() -> str:
    with importlib.resources.open_text("uapi", "internal.uapi.json") as stream:
        return "\n".join(stream.readlines())


def get_mock_uapi_json() -> str:
    with importlib.resources.open_text("uapi", "mock-internal.uapi.json") as stream:
        return "\n".join(stream.readlines())


def as_int(obj: Any) -> int:
    if obj is None or not isinstance(obj, int) or isinstance(obj, bool):
        raise TypeError
    return obj


def as_string(obj: Any) -> str:
    if obj is None or not isinstance(obj, str):
        raise TypeError
    return obj


def as_list(obj: Any) -> List[Any]:
    if obj is None or not isinstance(obj, list):
        raise TypeError
    return obj


def as_map(obj: Any) -> Dict[str, Any]:
    if obj is None or not isinstance(obj, dict):
        raise TypeError
    return obj


def offset_schema_index(initial_failures: List[_types._SchemaParseFailure], offset: int) -> List[_types._SchemaParseFailure]:
    final_list = []

    for f in initial_failures:
        reason = f.reason
        path = f.path
        data = f.data
        new_path = list(path)
        new_path[0] = new_path[0] - offset

        if reason == "PathCollision":
            other_new_path = list(data["other"])
            other_new_path[0] = other_new_path[0] - offset
            final_data = {"other": other_new_path}
        else:
            final_data = data

        final_list.append(_types._SchemaParseFailure(
            new_path, reason, final_data))

    return final_list


def find_schema_key(definition: dict[str, Any], index: int) -> str:
    import re

    regex = "^((fn|error|info|headers)|((struct|union|_ext)(<[0-2]>)?))\\..*"
    matches = []

    for e in definition.keys():
        if re.match(regex, e):
            matches.append(e)

    if len(matches) == 1:
        return matches[0]
    else:
        raise types.UApiSchemaParseError([_types._SchemaParseFailure([index], "ObjectKeyRegexMatchCountUnexpected",
                                                                     {"regex": regex, "actual": len(matches), "expected": 1})])


def find_matching_schema_key(schema_keys: Set[str], schema_key: str) -> Union[str, None]:
    for k in schema_keys:
        split_k = k.split(".")[1]
        split_schema_key = schema_key.split(".")[1]
        if split_k == split_schema_key:
            return k
    return None


def get_type_unexpected_parse_failure(path: List[Any], value: Any, expected_type: str) -> List[_types._SchemaParseFailure]:
    actual_type = get_type(value)
    data = {"actual": {actual_type: {}}, "expected": {expected_type: {}}}
    return [_types._SchemaParseFailure(path, "TypeUnexpected", data)]


def prepend(value: Any, original: List[Any]) -> List[Any]:
    new_list = list(original)
    new_list.insert(0, value)
    return new_list


def append(original: List[Any], value: Any) -> List[Any]:
    new_list = list(original)
    new_list.append(value)
    return new_list


def parse_type_declaration(path: List[Any], type_declaration_array: List[Any], this_type_parameter_count: int,
                           u_api_schema_pseudo_json: List[Any], schema_keys_to_index: Dict[str, int],
                           parsed_types: Dict[str, _types._UType], type_extensions: Dict[str, _types._UType],
                           all_parse_failures: List[_types._SchemaParseFailure], failed_types: Set[str]) -> _types._UTypeDeclaration:
    if not type_declaration_array:
        raise types.UApiSchemaParseError(
            [_types._SchemaParseFailure(path, "EmptyArrayDisallowed", {})])

    base_path = append(path, 0)
    base_type = type_declaration_array[0]

    try:
        root_type_string = as_string(base_type)
    except TypeError as e:
        this_parse_failures = get_type_unexpected_parse_failure(
            base_path, base_type, "String")
        raise types.UApiSchemaParseError(this_parse_failures)

    regex_string = "^(.+?)(\\?)?$"
    regex = re.compile(regex_string)

    matcher = regex.search(root_type_string)
    if not matcher:
        raise types.UApiSchemaParseError([_types._SchemaParseFailure(
            base_path, "StringRegexMatchFailed", {"regex": regex_string})])

    type_name = matcher.group(1)
    nullable = matcher.group(2) is not None

    type_obj = get_or_parse_type(base_path, type_name, this_type_parameter_count, u_api_schema_pseudo_json,
                                 schema_keys_to_index, parsed_types, type_extensions, all_parse_failures, failed_types)

    if isinstance(type_obj, _types._UGeneric) and nullable:
        raise types.UApiSchemaParseError([_types._SchemaParseFailure(
            base_path, "StringRegexMatchFailed", {"regex": "^(.+?)[^\\?]$"})])

    given_type_parameter_count = len(type_declaration_array) - 1
    if type_obj.get_type_parameter_count() != given_type_parameter_count:
        raise types.UApiSchemaParseError([_types._SchemaParseFailure(path, "ArrayLengthUnexpected",
                                                                     {"actual": len(type_declaration_array),
                                                                      "expected": type_obj.get_type_parameter_count() + 1})])

    parse_failures = []
    type_parameters = []
    given_type_parameters = type_declaration_array[1:]

    index = 0
    for e in given_type_parameters:
        index += 1
        loop_path = append(path, index)

        try:
            l = as_list(e)
        except TypeError as e1:
            this_parse_failures = get_type_unexpected_parse_failure(
                loop_path, e, "Array")
            parse_failures.extend(this_parse_failures)
            continue

        try:
            type_parameter_type_declaration = parse_type_declaration(loop_path, l, this_type_parameter_count,
                                                                     u_api_schema_pseudo_json, schema_keys_to_index,
                                                                     parsed_types, type_extensions, all_parse_failures,
                                                                     failed_types)
            type_parameters.append(type_parameter_type_declaration)
        except types.UApiSchemaParseError as e2:
            parse_failures.extend(e2.schema_parse_failures)

    if parse_failures:
        raise types.UApiSchemaParseError(parse_failures)

    return _types._UTypeDeclaration(type_obj, nullable, type_parameters)


def get_or_parse_type(path: List[Any], type_name: str, this_type_parameter_count: int,
                      u_api_schema_pseudo_json: List[Any], schema_keys_to_index: Dict[str, int],
                      parsed_types: Dict[str, _types._UType], type_extensions: Dict[str, _types._UType],
                      all_parse_failures: List[_types._SchemaParseFailure], failed_types: Set[str]) -> _types._UType:
    if type_name in failed_types:
        raise types.UApiSchemaParseError([])

    existing_type = parsed_types.get(type_name)
    if existing_type:
        return existing_type

    if this_type_parameter_count > 0:
        generic_regex = "|(T.([%s]))" % (
            "0-%d" % (this_type_parameter_count - 1) if this_type_parameter_count > 1 else "0")
    else:
        generic_regex = ""

    regex_string = "^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*)%s)$" % generic_regex
    regex = re.compile(regex_string)

    matcher = regex.search(type_name)
    if not matcher:
        raise types.UApiSchemaParseError([_types._SchemaParseFailure(path, "StringRegexMatchFailed", {
            "regex": regex_string})])

    standard_type_name = matcher.group(1)
    if standard_type_name:
        return {
            "boolean": _types._UBoolean(),
            "integer": _types._UInteger(),
            "number": _types._UNumber(),
            "string": _types._UString(),
            "array": _types._UArray(),
            "object": _types._UObject(),
        }.get(standard_type_name, _types._UAny())

    if this_type_parameter_count > 0:
        generic_parameter_index_string = matcher.group(9)
        if generic_parameter_index_string:
            generic_parameter_index = int(generic_parameter_index_string)
            return _types._UGeneric(generic_parameter_index)

    custom_type_name = matcher.group(2)
    index = schema_keys_to_index.get(custom_type_name)
    if index is None:
        raise types.UApiSchemaParseError([_types._SchemaParseFailure(
            path, "TypeUnknown", {"name": custom_type_name})])

    definition = u_api_schema_pseudo_json[index]

    type_parameter_count_string = matcher.group(6)
    type_parameter_count = int(
        type_parameter_count_string) if type_parameter_count_string else 0

    try:

        if custom_type_name.startswith("struct"):
            t = parse_struct_type([index], definition, custom_type_name, [], type_parameter_count,
                                  u_api_schema_pseudo_json, schema_keys_to_index, parsed_types, type_extensions,
                                  all_parse_failures, failed_types)
        elif custom_type_name.startswith("union"):
            is_for_fn = False
            t = parse_union_type([index], definition, custom_type_name, is_for_fn, type_parameter_count,
                                 u_api_schema_pseudo_json, schema_keys_to_index, parsed_types, type_extensions,
                                 all_parse_failures, failed_types)
        elif custom_type_name.startswith("fn"):
            t = parse_function_type([index], definition, custom_type_name, u_api_schema_pseudo_json,
                                    schema_keys_to_index, parsed_types, type_extensions, all_parse_failures,
                                    failed_types)
        else:
            t = type_extensions.get(custom_type_name)
            if not t:
                raise types.UApiSchemaParseError([_types._SchemaParseFailure([index], "TypeExtensionImplementationMissing",
                                                                             {"name": custom_type_name})])

        parsed_types[custom_type_name] = t

        return t
    except types.UApiSchemaParseError as e:
        all_parse_failures.extend(e.schema_parse_failures)
        failed_types.add(custom_type_name)
        raise types.UApiSchemaParseError([])


def parse_struct_type(path: List[object], struct_definition_as_pseudo_json: Dict[str, object],
                      schema_key: str, ignore_keys: List[str], type_parameter_count: int,
                      uapi_schema_pseudo_json: List[object], schema_keys_to_index: Dict[str, int],
                      parsed_types: Dict[str, _types._UType], type_extensions: Dict[str, _types._UType],
                      all_parse_failures: List[_types._SchemaParseFailure], failed_types: Set[str]) -> _types._UStruct:
    parse_failures = []

    other_keys = set(struct_definition_as_pseudo_json.keys())
    other_keys.discard(schema_key)
    other_keys.discard("///")
    other_keys.discard("ignoreIfDuplicate")

    for ignore_key in ignore_keys:
        other_keys.discard(ignore_key)

    if other_keys:
        for k in other_keys:
            loop_path = path + [k]
            parse_failures.append(_types._SchemaParseFailure(
                loop_path, "ObjectKeyDisallowed", {}))

    this_path = path + [schema_key]
    def_init = struct_definition_as_pseudo_json.get(schema_key)

    try:
        definition = as_map(def_init)
    except TypeError:
        branch_parse_failures = get_type_unexpected_parse_failure(
            this_path, def_init, "Object")
        parse_failures.extend(branch_parse_failures)

    if parse_failures:
        raise types.UApiSchemaParseError(parse_failures)

    fields = parse_struct_fields(definition, this_path, type_parameter_count,
                                 uapi_schema_pseudo_json, schema_keys_to_index, parsed_types,
                                 type_extensions, all_parse_failures, failed_types)

    return _types._UStruct(schema_key, fields, type_parameter_count)


def parse_union_type(path: List[object], union_definition_as_pseudo_json: Dict[str, object],
                     schema_key: str, is_for_fn: bool, type_parameter_count: int,
                     uapi_schema_pseudo_json: List[object], schema_keys_to_index: Dict[str, int],
                     parsed_types: Dict[str, _types._UType], type_extensions: Dict[str, _types._UType],
                     all_parse_failures: List[_types._SchemaParseFailure], failed_types: Set[str]) -> _types._UUnion:
    parse_failures = []

    other_keys = set(union_definition_as_pseudo_json.keys())
    other_keys.discard(schema_key)
    other_keys.discard("///")

    if not is_for_fn and other_keys:
        for k in other_keys:
            loop_path = path + [k]
            parse_failures.append(_types._SchemaParseFailure(
                loop_path, "ObjectKeyDisallowed", {}))

    this_path = path + [schema_key]
    def_init = union_definition_as_pseudo_json.get(schema_key)

    try:
        definition = as_map(def_init)
    except TypeError:
        final_parse_failures = get_type_unexpected_parse_failure(
            this_path, def_init, "Object")
        parse_failures.extend(final_parse_failures)
        raise types.UApiSchemaParseError(parse_failures)

    cases = {}

    if not definition and not is_for_fn:
        parse_failures.append(_types._SchemaParseFailure(
            this_path, "EmptyObjectDisallowed", {}))
    elif is_for_fn and "Ok" not in definition:
        branch_path = this_path + ["Ok"]
        parse_failures.append(_types._SchemaParseFailure(
            branch_path, "RequiredObjectKeyMissing", {}))

    for union_case, entry_value in definition.items():
        union_key_path = this_path + [union_case]
        regex_string = r"^(_?[A-Z][a-zA-Z0-9_]*)$"
        regex = re.compile(regex_string)
        matcher = regex.search(union_case)

        if not matcher:
            parse_failures.append(_types._SchemaParseFailure(union_key_path, "KeyRegexMatchFailed",
                                                             {"regex": regex_string}))
            continue

        try:
            union_case_struct = as_map(entry_value)
        except TypeError:
            this_parse_failures = get_type_unexpected_parse_failure(
                union_key_path, entry_value, "Object")
            parse_failures.extend(this_parse_failures)
            continue

        try:
            fields = parse_struct_fields(union_case_struct, union_key_path, type_parameter_count,
                                         uapi_schema_pseudo_json, schema_keys_to_index, parsed_types,
                                         type_extensions, all_parse_failures, failed_types)
        except types.UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)
            continue

        union_struct = _types._UStruct(
            f"{schema_key}.{union_case}", fields, type_parameter_count)
        cases[union_case] = union_struct

    if parse_failures:
        raise types.UApiSchemaParseError(parse_failures)

    return _types._UUnion(schema_key, cases, type_parameter_count)


def parse_struct_fields(reference_struct: Dict[str, object], path: List[object],
                        type_parameter_count: int, uapi_schema_pseudo_json: List[object],
                        schema_keys_to_index: Dict[str, int], parsed_types: Dict[str, _types._UType],
                        type_extensions: Dict[str, _types._UType], all_parse_failures: List[_types._SchemaParseFailure],
                        failed_types: Set[str]) -> Dict[str, _types._UFieldDeclaration]:
    parse_failures = []
    fields = {}

    for struct_entry_key, struct_entry_value in reference_struct.items():
        field_declaration = struct_entry_key

        for existing_field in fields.keys():
            existing_field_no_opt = existing_field.split("!")[0]
            field_no_opt = field_declaration.split("!")[0]

            if field_no_opt == existing_field_no_opt:
                final_path = path + [field_declaration]
                final_other_path = path + [existing_field]
                parse_failures.append(_types._SchemaParseFailure(final_path, "PathCollision",
                                                                 {"other": final_other_path}))

        type_declaration_value = struct_entry_value

        try:
            parsed_field = parse_field(path, field_declaration,
                                       type_declaration_value, type_parameter_count, uapi_schema_pseudo_json,
                                       schema_keys_to_index, parsed_types,
                                       type_extensions, all_parse_failures, failed_types)
            field_name = parsed_field.field_name

            fields[field_name] = parsed_field
        except types.UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise types.UApiSchemaParseError(parse_failures)

    return fields


def parse_field(path: List[object], field_declaration: str, type_declaration_value: object,
                type_parameter_count: int, uapi_schema_pseudo_json: List[object],
                schema_keys_to_index: Dict[str, int], parsed_types: Dict[str, _types._UType],
                type_extensions: Dict[str, _types._UType], all_parse_failures: List[_types._SchemaParseFailure],
                failed_types: Set[str]) -> _types._UFieldDeclaration:
    regex_string = r"^(_?[a-z][a-zA-Z0-9_]*)(!)?$"
    regex = re.compile(regex_string)

    matcher = regex.search(field_declaration)
    if not matcher:
        final_path = path + [field_declaration]
        raise types.UApiSchemaParseError([_types._SchemaParseFailure(
            final_path, "KeyRegexMatchFailed", {"regex": regex_string})])

    field_name = matcher.group(0)
    optional = matcher.group(2) is not None
    this_path = path + [field_name]

    try:
        type_declaration_array = as_list(type_declaration_value)
    except TypeError:
        raise types.UApiSchemaParseError(get_type_unexpected_parse_failure(
            this_path, type_declaration_value, "Array"))

    type_declaration = parse_type_declaration(this_path, type_declaration_array, type_parameter_count,
                                              uapi_schema_pseudo_json, schema_keys_to_index, parsed_types,
                                              type_extensions, all_parse_failures, failed_types)

    return _types._UFieldDeclaration(field_name, type_declaration, optional)


def apply_error_to_parsed_types(error: _types._UError, parsed_types: Dict[str, _types._UType],
                                schema_keys_to_index: Dict[str, int]) -> None:
    import pprint
    error_name = error.name
    error_index = schema_keys_to_index.get(error_name)

    parse_failures = []
    for parsed_type_name, parsed_type in parsed_types.items():
        if not isinstance(parsed_type, _types._UFn):
            continue

        f: _types._UFn = parsed_type
        fn_name = f.name

        regex = re.compile(f.errors_regex)
        matcher = regex.search(error_name)
        if not matcher:
            continue

        fn_result = f.result
        fn_result_cases = fn_result.cases
        error_fn_result = error.errors
        error_fn_result_cases = error_fn_result.cases

        for error_result_field, error_result_struct in error_fn_result_cases.items():
            new_key = error_result_field
            if new_key in fn_result_cases:
                other_path_index = schema_keys_to_index.get(fn_name)
                parse_failures.append(_types._SchemaParseFailure([error_index, error_name, "->", new_key],
                                                                 "PathCollision", {"other": [other_path_index, "->", new_key]}))

            fn_result_cases[new_key] = error_result_struct

    if parse_failures:
        raise types.UApiSchemaParseError(parse_failures)


def parse_error_type(error_definition_as_parsed_json: Dict[str, object], schema_key: str,
                     uapi_schema_pseudo_json: List[object], schema_keys_to_index: Dict[str, int],
                     parsed_types: Dict[str, _types._UType], type_extensions: Dict[str, _types._UType],
                     all_parse_failures: List[_types._SchemaParseFailure], failed_types: Set[str]) -> _types._UError:
    index = schema_keys_to_index.get(schema_key)
    base_path = [index]

    parse_failures = []

    other_keys = set(error_definition_as_parsed_json.keys())
    other_keys.discard(schema_key)
    other_keys.discard("///")

    if other_keys:
        for k in other_keys:
            loop_path = base_path + [k]
            parse_failures.append(_types._SchemaParseFailure(
                loop_path, "ObjectKeyDisallowed", {}))

    def_init = error_definition_as_parsed_json.get(schema_key)
    this_path = base_path + [schema_key]

    try:
        def_dict = as_map(def_init)
    except TypeError:
        this_parse_failures = get_type_unexpected_parse_failure(
            this_path, def_init, "Object")
        parse_failures.extend(this_parse_failures)
        raise types.UApiSchemaParseError(parse_failures)

    result_schema_key = "->"
    ok_case_required = False
    type_parameter_count = 0
    error_path = this_path + [result_schema_key]

    if result_schema_key not in def_dict:
        parse_failures.append(_types._SchemaParseFailure(
            error_path, "RequiredObjectKeyMissing", {}))

    if parse_failures:
        raise types.UApiSchemaParseError(parse_failures)

    error = parse_union_type(this_path, def_dict, result_schema_key, ok_case_required, type_parameter_count,
                             uapi_schema_pseudo_json, schema_keys_to_index, parsed_types, type_extensions,
                             all_parse_failures, failed_types)

    return _types._UError(schema_key, error)


def parse_headers_type(headers_definition_as_parsed_json: Dict[str, object],
                        schema_key: str, uapi_schema_pseudo_json: List[object], schema_keys_to_index: Dict[str, int],
                        parsed_types: Dict[str, _types._UType], type_extensions: Dict[str, _types._UType],
                        all_parse_failures: List[_types._SchemaParseFailure], failed_types: Set[str]) -> _types._UHeaders:
    index = schema_keys_to_index.get(schema_key)
    path = [index]

    parse_failures = []
    type_parameter_count = 0

    request_headers_struct = None
    try:
        request_headers_struct = parse_struct_type(path, headers_definition_as_parsed_json, schema_key, ['->'],
                                     type_parameter_count, uapi_schema_pseudo_json, schema_keys_to_index,
                                     parsed_types, type_extensions, all_parse_failures, failed_types)
        
        for key, field in request_headers_struct.fields.items():
            if field.optional:
                this_path = append(append(path, schema_key), key)
                regex_string = '^(_?[a-z][a-zA-Z0-9_]*)$'
                parse_failures.append(_types._SchemaParseFailure(this_path, 'KeyRegexMatchFailed', {'regex': regex_string}))

    except types.UApiSchemaParseError as e:
        parse_failures.extend(e.schema_parse_failures)

    result_schema_key = "->"
    res_path = path + [result_schema_key]

    response_headers_struct = None
    if result_schema_key not in headers_definition_as_parsed_json:
        parse_failures.append(_types._SchemaParseFailure(
            res_path, "RequiredObjectKeyMissing", {}))
    else:
        try:
            response_headers_struct = parse_struct_type(path, headers_definition_as_parsed_json, result_schema_key, [schema_key],
                                        type_parameter_count, uapi_schema_pseudo_json, schema_keys_to_index,
                                        parsed_types, type_extensions, all_parse_failures, failed_types)
            
            for key, field in response_headers_struct.fields.items():
                if field.optional:
                    this_path = append(append(path, schema_key), key)
                    regex_string = '^(_?[a-z][a-zA-Z0-9_]*)$'
                    parse_failures.append(_types._SchemaParseFailure(this_path, 'KeyRegexMatchFailed', {'regex': regex_string}))

        except types.UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise types.UApiSchemaParseError(parse_failures)

    return _types._UHeaders(schema_key, request_headers_struct.fields, response_headers_struct.fields)


def parse_function_type(path: List[object], function_definition_as_parsed_json: Dict[str, object],
                        schema_key: str, uapi_schema_pseudo_json: List[object], schema_keys_to_index: Dict[str, int],
                        parsed_types: Dict[str, _types._UType], type_extensions: Dict[str, _types._UType],
                        all_parse_failures: List[_types._SchemaParseFailure], failed_types: Set[str]) -> _types._UFn:
    parse_failures = []
    type_parameter_count = 0
    is_for_fn = True

    call_type = None
    try:
        arg_type = parse_struct_type(path, function_definition_as_parsed_json, schema_key, ['->', 'errors'],
                                     type_parameter_count, uapi_schema_pseudo_json, schema_keys_to_index,
                                     parsed_types, type_extensions, all_parse_failures, failed_types)
        call_type = _types._UUnion(
            schema_key, {schema_key: arg_type}, type_parameter_count)
    except types.UApiSchemaParseError as e:
        parse_failures.extend(e.schema_parse_failures)

    result_schema_key = "->"
    res_path = path + [result_schema_key]

    result_type = None
    if result_schema_key not in function_definition_as_parsed_json:
        parse_failures.append(_types._SchemaParseFailure(
            res_path, "RequiredObjectKeyMissing", {}))
    else:
        try:
            result_type = parse_union_type(path, function_definition_as_parsed_json, result_schema_key, is_for_fn,
                                           type_parameter_count, uapi_schema_pseudo_json, schema_keys_to_index,
                                           parsed_types, type_extensions, all_parse_failures, failed_types)
        except types.UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    errors_regex_key = "errors"
    regex_path = path + [errors_regex_key]

    errors_regex = None
    if errors_regex_key in function_definition_as_parsed_json and not schema_key.startswith("fn._"):
        parse_failures.append(_types._SchemaParseFailure(
            regex_path, "ObjectKeyDisallowed", {}))
    else:
        errors_regex_init = function_definition_as_parsed_json.get(
            errors_regex_key, "^error\\..*$")
        try:
            errors_regex = as_string(errors_regex_init)
        except TypeError:
            this_parse_failures = get_type_unexpected_parse_failure(
                regex_path, errors_regex_init, "String")
            parse_failures.extend(this_parse_failures)

    if parse_failures:
        raise types.UApiSchemaParseError(parse_failures)

    return _types._UFn(schema_key, call_type, result_type, errors_regex)


def new_uapi_schema(uapi_schema_json: str, type_extensions: Dict[str, Any]) -> 'types.UApiSchema':
    try:
        uapi_schema_pseudo_json_init = json.loads(uapi_schema_json)
    except json.JSONDecodeError as e:
        raise types.UApiSchemaParseError(
            [_types._SchemaParseFailure([], "JsonInvalid", {})], e)

    try:
        uapi_schema_pseudo_json = as_list(uapi_schema_pseudo_json_init)
    except TypeError as e:
        this_parse_failures = get_type_unexpected_parse_failure(
            [], uapi_schema_pseudo_json_init, "Array")
        raise types.UApiSchemaParseError(this_parse_failures, e)

    return parse_uapi_schema(uapi_schema_pseudo_json, type_extensions, 0)


def extend_uapi_schema(first: 'types.UApiSchema', second_uapi_schema_json: str, second_type_extensions: Dict[str, Any]) -> 'types.UApiSchema':
    try:
        second_uapi_schema_pseudo_json_init = json.loads(
            second_uapi_schema_json)
    except json.JSONDecodeError as e:
        raise types.UApiSchemaParseError(
            [_types._SchemaParseFailure([], "JsonInvalid", {})], e)

    try:
        second_uapi_schema_pseudo_json = as_list(
            second_uapi_schema_pseudo_json_init)
    except TypeError as e:
        this_parse_failure = get_type_unexpected_parse_failure(
            [], second_uapi_schema_pseudo_json_init, "Array")
        raise types.UApiSchemaParseError(this_parse_failure, e)

    first_original = first.original
    first_type_extensions = first.type_extensions

    original = first_original + second_uapi_schema_pseudo_json

    type_extensions = first_type_extensions.copy()
    type_extensions.update(second_type_extensions)

    return parse_uapi_schema(original, type_extensions, len(first_original))


def parse_uapi_schema(uapi_schema_pseudo_json: List[object], type_extensions: Dict[str, Any], path_offset: int) -> 'types.UApiSchema':
    parsed_types: Dict[str, Any] = {}
    parse_failures: List[_types._SchemaParseFailure] = []
    failed_types: Set[str] = set()
    schema_keys_to_index: Dict[str, int] = {}
    schema_keys: Set[str] = set()

    index = -1
    for definition in uapi_schema_pseudo_json:
        index += 1

        loop_path = [index]

        try:
            def_dict = as_map(definition)
        except TypeError as e:
            this_parse_failures = get_type_unexpected_parse_failure(
                loop_path, definition, "Object")
            parse_failures.extend(this_parse_failures)
            continue

        try:
            schema_key = find_schema_key(def_dict, index)
        except types.UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)
            continue

        ignore_if_duplicate: bool = def_dict.get('ignoreIfDuplicate', False)
        matching_schema_key = find_matching_schema_key(schema_keys, schema_key)
        if matching_schema_key and not ignore_if_duplicate:
            other_path_index = schema_keys_to_index[matching_schema_key]
            final_path = loop_path + [schema_key]
            parse_failures.append(_types._SchemaParseFailure(final_path, "PathCollision", {
                                  "other": [other_path_index, matching_schema_key]}))
            continue

        schema_keys.add(schema_key)
        schema_keys_to_index[schema_key] = index

    if parse_failures:
        offset_parse_failures = offset_schema_index(
            parse_failures, path_offset)
        raise types.UApiSchemaParseError(offset_parse_failures)

    error_keys = set()
    header_keys = set()
    root_type_parameter_count = 0

    for schema_key in schema_keys:
        if schema_key.startswith("info."):
            continue
        elif schema_key.startswith("error."):
            error_keys.add(schema_key)
            continue
        elif schema_key.startswith("headers."):
            header_keys.add(schema_key)
            continue

        this_index = schema_keys_to_index[schema_key]

        try:
            get_or_parse_type([this_index], schema_key, root_type_parameter_count, uapi_schema_pseudo_json,
                              schema_keys_to_index, parsed_types, type_extensions, parse_failures, failed_types)
        except types.UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        offset_parse_failures = offset_schema_index(
            parse_failures, path_offset)
        raise types.UApiSchemaParseError(offset_parse_failures)
    
    for error_key in error_keys:
        this_index = schema_keys_to_index[error_key]
        def_dict = uapi_schema_pseudo_json[this_index]

        try:
            error = parse_error_type(def_dict, error_key, uapi_schema_pseudo_json, schema_keys_to_index, parsed_types,
                                     type_extensions, parse_failures, failed_types)
            apply_error_to_parsed_types(
                error, parsed_types, schema_keys_to_index)
        except types.UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    request_headers: Dict[str, _types._UFieldDeclaration] = {}
    response_headers: Dict[str, _types._UFieldDeclaration] = {}

    for header_key in header_keys:
        this_index = schema_keys_to_index[header_key]
        def_dict = uapi_schema_pseudo_json[this_index]

        try:
            headers_type = parse_headers_type(def_dict, header_key, uapi_schema_pseudo_json, schema_keys_to_index, parsed_types,
                                     type_extensions, parse_failures, failed_types)
            
            print(f'headers_type {headers_type}')
            
            request_headers.update(headers_type.request_headers)
            response_headers.update(headers_type.response_headers)

        except types.UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        offset_parse_failures = offset_schema_index(
            parse_failures, path_offset)
        raise types.UApiSchemaParseError(offset_parse_failures)

    return types.UApiSchema(uapi_schema_pseudo_json, parsed_types, request_headers, response_headers, type_extensions)


class _BinaryPackNode:
    def __init__(self, value: int, nested: Dict[int, '_BinaryPackNode']):
        self.value = value
        self.nested = nested


PACKED_BYTE: int = 17
UNDEFINED_BYTE: int = 18


def pack_body(body: Dict[Any, Any]) -> Dict[Any, Any]:
    result: Dict[Any, Any] = {}

    for key, value in body.items():
        packed_value = pack(value)
        result[key] = packed_value

    return result


def pack(value: Any) -> Any:
    if isinstance(value, list):
        return pack_list(value)
    elif isinstance(value, dict):
        new_map: Dict[Any, Any] = {}

        for k, v in value.items():
            new_map[k] = pack(v)

        return new_map
    else:
        return value


class CannotPack(Exception):
    pass


def pack_list(lst: List[Any]) -> List[Any]:
    if not lst:
        return lst

    packed_list: List[Any] = []
    header: List[Any] = []

    packed_list.append(ExtType(PACKED_BYTE, bytes()))

    header.append(None)

    packed_list.append(header)

    key_index_map: Dict[int, _BinaryPackNode] = {}
    try:
        for e in lst:
            if isinstance(e, dict):
                row = pack_map(e, header, key_index_map)
                packed_list.append(row)
            else:
                raise CannotPack()
        return packed_list
    except CannotPack:
        new_list = [pack(e) for e in lst]
        return new_list


def pack_map(m: Dict[Any, Any], header: List[Any], key_index_map: Dict[int, _BinaryPackNode]) -> List[Any]:
    row: List[Any] = []
    for key, value in m.items():
        if isinstance(key, str):
            raise CannotPack()

        key = int(key)
        key_index = key_index_map.get(key)

        if key_index is None:
            final_key_index = _BinaryPackNode(len(header) - 1, {})

            if isinstance(value, dict):
                header.append([key])
            else:
                header.append(key)

            key_index_map[key] = final_key_index
        else:
            final_key_index = key_index

        key_index_value = final_key_index.value
        key_index_nested = final_key_index.nested

        if isinstance(value, dict):
            nested_header = header[key_index_value + 1]
            if nested_header == None or not isinstance(nested_header, list):
                # No nesting available, so the data structure is inconsistent
                raise CannotPack()

            packed_value = pack_map(value, nested_header, key_index_nested)
        else:
            if isinstance(header[key_index_value + 1], list):
                raise CannotPack()

            packed_value = pack(value)

        while len(row) < key_index_value:
            row.append(ExtType(UNDEFINED_BYTE, bytes()))

        if len(row) == key_index_value:
            row.append(packed_value)
        else:
            row[key_index_value] = packed_value

    return row


def unpack_body(body: Dict[Any, Any]) -> Dict[Any, Any]:
    result: Dict[Any, Any] = {}

    for key, value in body.items():
        unpacked_value = unpack(value)
        result[key] = unpacked_value

    return result


def unpack(value: Any) -> Any:
    if isinstance(value, list):
        return unpack_list(value)
    elif isinstance(value, dict):
        new_map: Dict[Any, Any] = {}

        for k, v in value.items():
            new_map[k] = unpack(v)

        return new_map
    else:
        return value


def unpack_list(lst: List[Any]) -> List[Any]:
    if not lst:
        return lst

    if isinstance(lst[0], ExtType) and lst[0].code == PACKED_BYTE:
        unpacked_list: List[Any] = []
        headers = lst[1]

        for i in range(2, len(lst)):
            row = lst[i]
            m = unpack_map(row, headers)
            unpacked_list.append(m)

        return unpacked_list
    else:
        new_list = [unpack(e) for e in lst]
        return new_list


def unpack_map(row: List[Any], header: List[Any]) -> Dict[int, Any]:
    final_map: Dict[int, Any] = {}

    for j in range(len(row)):
        key = header[j + 1]
        value = row[j]

        if isinstance(value, ExtType) and value.code == UNDEFINED_BYTE:
            continue

        if isinstance(key, int):
            unpacked_value = unpack(value)

            final_map[key] = unpacked_value
        else:
            nested_header = key
            nested_row = value
            m = unpack_map(nested_row, nested_header)
            i = nested_header[0]

            final_map[i] = m

    return final_map


def server_binary_encode(message: List[Any], binary_encoder: _types._BinaryEncoding) -> List[Any]:
    headers: dict[str, Any] = message[0]
    message_body = message[1]
    client_known_binary_checksums: list[int] = headers.pop(
        "_clientKnownBinaryChecksums", None)

    if client_known_binary_checksums is None or binary_encoder.checksum not in client_known_binary_checksums:
        headers["_enc"] = binary_encoder.encode_map

    headers["_bin"] = [binary_encoder.checksum]
    encoded_message_body = encode_body(message_body, binary_encoder)

    final_encoded_message_body = pack_body(
        encoded_message_body) if headers.get("_pac") else encoded_message_body

    return [headers, final_encoded_message_body]


def server_binary_decode(message: List[Any], binary_encoder: _types._BinaryEncoding) -> List[Any]:
    headers = message[0]
    encoded_message_body = message[1]
    client_known_binary_checksums = headers["_bin"]
    binary_checksum_used_by_client_on_this_message = client_known_binary_checksums[0]

    if binary_checksum_used_by_client_on_this_message != binary_encoder.checksum:
        raise _types._BinaryEncoderUnavailableError()

    final_encoded_message_body = unpack_body(
        encoded_message_body) if headers.get("_pac") else encoded_message_body

    message_body = decode_body(final_encoded_message_body, binary_encoder)
    return [headers, message_body]


def client_binary_encode(message: List[Any], recent_binary_encoders: Dict[int, _types._BinaryEncoding],
                         binary_checksum_strategy: 'types.ClientBinaryStrategy') -> List[Any]:
    headers: dict[str, Any] = message[0]
    message_body = message[1]
    force_send_json = headers.pop("_forceSendJson", None)

    headers["_bin"] = binary_checksum_strategy.get_current_checksums()

    if force_send_json:
        raise _types._BinaryEncoderUnavailableError()

    if len(recent_binary_encoders) > 1:
        raise _types._BinaryEncoderUnavailableError()

    checksums = list(recent_binary_encoders.keys())
    try:
        binary_encoder = recent_binary_encoders[checksums[0]]
    except IndexError:
        raise _types._BinaryEncoderUnavailableError()

    encoded_message_body = encode_body(message_body, binary_encoder)

    final_encoded_message_body = pack_body(
        encoded_message_body) if headers.get("_pac") else encoded_message_body

    return [headers, final_encoded_message_body]


def client_binary_decode(message: List[Any], recent_binary_encoders: Dict[int, _types._BinaryEncoding],
                         binary_checksum_strategy: 'types.ClientBinaryStrategy') -> List[Any]:
    headers = message[0]
    encoded_message_body = message[1]
    binary_checksums = headers["_bin"]
    binary_checksum = binary_checksums[0]

    if "_enc" in headers:
        binary_encoding = headers["_enc"]
        new_binary_encoder = _types._BinaryEncoding(
            binary_encoding, binary_checksum)
        recent_binary_encoders[binary_checksum] = new_binary_encoder

    binary_checksum_strategy.update(binary_checksum)
    new_current_checksum_strategy = binary_checksum_strategy.get_current_checksums()

    for key in list(recent_binary_encoders.keys()):
        if key not in new_current_checksum_strategy:
            del recent_binary_encoders[key]

    binary_encoder = recent_binary_encoders[binary_checksum]

    final_encoded_message_body = unpack_body(
        encoded_message_body) if headers.get("_pac") else encoded_message_body

    message_body = decode_body(final_encoded_message_body, binary_encoder)
    return [headers, message_body]


def encode_body(message_body: Dict[str, Any], binary_encoder: _types._BinaryEncoding) -> Dict[Any, Any]:
    return encode_keys(message_body, binary_encoder)


def decode_body(encoded_message_body: Dict[Any, Any], binary_encoder: _types._BinaryEncoding) -> Dict[str, Any]:
    return decode_keys(encoded_message_body, binary_encoder)


def encode_keys(given: Any, binary_encoder: _types._BinaryEncoding) -> Any:
    if given is None:
        return given
    elif isinstance(given, dict):
        new_map = {}
        for key, value in given.items():
            final_key = binary_encoder.encode_map.get(key, key)
            encoded_value = encode_keys(value, binary_encoder)
            new_map[final_key] = encoded_value
        return new_map
    elif isinstance(given, list):
        return [encode_keys(e, binary_encoder) for e in given]
    else:
        return given


def decode_keys(given: Any, binary_encoder: _types._BinaryEncoding) -> Any:
    if isinstance(given, dict):
        new_map = {}
        for key, value in given.items():
            if isinstance(key, str):
                decoded_key = key
            else:
                if key not in binary_encoder.decode_map:
                    raise _types._BinaryEncodingMissing(key)

                decoded_key = binary_encoder.decode_map[key]
            decoded_value = decode_keys(value, binary_encoder)
            new_map[decoded_key] = decoded_value
        return new_map
    elif isinstance(given, list):
        return [decode_keys(e, binary_encoder) for e in given]
    else:
        return given


def construct_binary_encoding(u_api_schema: 'types.UApiSchema') -> _types._BinaryEncoding:
    all_keys: Set[str] = set()

    for key, value in u_api_schema.parsed.items():
        all_keys.add(key)

        if isinstance(value, _types._UStruct):
            struct_fields: Dict[str, _types._UFieldDeclaration] = value.fields
            all_keys.update(struct_fields.keys())
        elif isinstance(value, _types._UUnion):
            union_cases: Dict[str, _types._UStruct] = value.cases
            for case_key, case_value in union_cases.items():
                all_keys.add(case_key)
                struct_fields = case_value.fields
                all_keys.update(struct_fields.keys())
        elif isinstance(value, _types._UFn):
            fn_call_cases: Dict[str, _types._UStruct] = value.call.cases
            fn_result_cases: Dict[str, _types._UStruct] = value.result.cases

            for case_key, case_value in fn_call_cases.items():
                all_keys.add(case_key)
                struct_fields = case_value.fields
                all_keys.update(struct_fields.keys())

            for case_key, case_value in fn_result_cases.items():
                all_keys.add(case_key)
                struct_fields = case_value.fields
                all_keys.update(struct_fields.keys())

    sorted_all_keys = sorted(all_keys)
    binary_encoding = {key: i for i, key in enumerate(sorted_all_keys)}
    final_string = "\n".join(sorted_all_keys)
    checksum = create_checksum(final_string)
    return _types._BinaryEncoding(binary_encoding, checksum)


def create_checksum(value: str) -> int:
    crc32_hash = int(binascii.crc32(value.encode('utf-8')) & 0xffffffff)
    return (crc32_hash ^ 0x80000000) - 0x80000000


def serialize(message: 'types.Message', binary_encoder: _types._BinaryEncoder, serializer: 'types.SerializationImpl') -> bytes:
    headers = message.header
    serialize_as_binary = headers.pop("_binary", False)

    message_as_pseudo_json = [message.header, message.body]

    try:
        if serialize_as_binary:
            try:
                encoded_message = binary_encoder.encode(message_as_pseudo_json)
                return serializer.to_msgpack(encoded_message)
            except _types._BinaryEncoderUnavailableError:
                return serializer.to_json(message_as_pseudo_json)
        else:
            return serializer.to_json(message_as_pseudo_json)
    except Exception as e:
        raise types.SerializationError() from e


def deserialize(message_bytes: bytes, serializer: 'types.SerializationImpl', binary_encoder: _types._BinaryEncoder) -> 'types.Message':
    is_msg_pack = message_bytes[0] == 0x92  # MsgPack
    message_as_pseudo_json = serializer.from_msgpack(
        message_bytes) if is_msg_pack else serializer.from_json(message_bytes)
    message_as_pseudo_json_list = list(message_as_pseudo_json)

    if len(message_as_pseudo_json_list) != 2:
        raise _types._InvalidMessage()

    final_message_as_pseudo_json_list = binary_encoder.decode(
        message_as_pseudo_json_list) if is_msg_pack else message_as_pseudo_json_list

    headers = final_message_as_pseudo_json_list[0]
    body = final_message_as_pseudo_json_list[1]

    if not isinstance(headers, dict) or not isinstance(body, dict):
        raise _types._InvalidMessage()

    if len(body) != 1:
        raise _types._InvalidMessageBody()

    try:
        payload = list(body.values())[0]
        if not isinstance(payload, dict):
            raise _types._InvalidMessageBody()
    except Exception:
        raise _types._InvalidMessageBody()

    return types.Message(headers, body)


def get_type(value: Any) -> str:
    if value is None:
        return "Null"
    elif isinstance(value, bool):
        return "Boolean"
    elif isinstance(value, (int, float)):
        return "Number"
    elif isinstance(value, str):
        return "String"
    elif isinstance(value, list):
        return "Array"
    elif isinstance(value, dict):
        return "Object"
    else:
        return "Unknown"


def get_type_unexpected_validation_failure(path: List[Any], value: Any, expected_type: str) -> List[_types._ValidationFailure]:
    actual_type = get_type(value)
    data = {
        "actual": {actual_type: {}},
        "expected": {expected_type: {}}
    }
    return [_types._ValidationFailure(path, "TypeUnexpected", data)]


def validate_headers(headers: Dict[str, Any], uapi_schema: 'types.UApiSchema', function_type: _types._UFn) -> List[_types._ValidationFailure]:
    validation_failures: List[_types._ValidationFailure] = []

    for header, header_value in headers.items():
        field = uapi_schema.parsed_request_headers.get(header, None)
        if field:
            this_validation_failures = field.type_declaration.validate(
                header_value,
                None,
                function_type.name,
                []
            )
            this_validation_failures_path = []
            for x in this_validation_failures:
                this_validation_failures_path.append(
                    _types._ValidationFailure(prepend(header, x.path), x.reason, x.data)
                )
            
            validation_failures.extend(this_validation_failures_path)

    return validation_failures


def validate_value_of_type(value: Any, select: Dict[str, object], fn: str, generics: List[_types._UTypeDeclaration], this_type: _types._UType, nullable: bool, type_parameters: List[_types._UTypeDeclaration]) -> List[_types._ValidationFailure]:
    if value is None:
        is_nullable = generics[this_type.index].nullable if isinstance(
            this_type, _types._UGeneric) else nullable
        if not is_nullable:
            return get_type_unexpected_validation_failure([], value, this_type.get_name(generics))
        else:
            return []
    else:
        return this_type.validate(value, select, fn, type_parameters, generics)


def generate_random_value_of_type(blueprint_value: Any, use_blueprint_value: bool, include_optional_fields: bool, randomize_optional_fields: bool, generics: List[_types._UTypeDeclaration], random_generator: _rg._RandomGenerator, this_type: _types._UType, nullable: bool, type_parameters: List[_types._UTypeDeclaration]) -> Any:
    if nullable and not use_blueprint_value and random_generator.next_boolean():
        return None
    else:
        return this_type.generate_random_value(blueprint_value, use_blueprint_value, include_optional_fields, randomize_optional_fields, type_parameters, generics, random_generator)


def generate_random_any(random_generator: _rg._RandomGenerator) -> Any:
    select_type = random_generator.next_int_with_ceiling(3)
    if select_type == 0:
        return random_generator.next_boolean()
    elif select_type == 1:
        return random_generator.next_int()
    else:
        return random_generator.next_string()


def validate_boolean(value: Any) -> List[_types._ValidationFailure]:
    if isinstance(value, bool):
        return []
    else:
        return get_type_unexpected_validation_failure([], value, _BOOLEAN_NAME)


def generate_random_boolean(blueprint_value: Any, use_blueprint_value: bool, random_generator: _rg._RandomGenerator) -> Any:
    if use_blueprint_value:
        return blueprint_value
    else:
        return random_generator.next_boolean()


def validate_integer(value: Any) -> List[_types._ValidationFailure]:
    if isinstance(value, (int)) and not isinstance(value, (bool, float)):
        if (value > 2**63-1 or value < -(2**63)):
            return [_types._ValidationFailure([], "NumberOutOfRange", {})]
        else:
            return []

    return get_type_unexpected_validation_failure([], value, _INTEGER_NAME)


def generate_random_integer(blueprint_value: Any, use_blueprint_value: bool,
                            random_generator: _rg._RandomGenerator) -> Any:
    if use_blueprint_value:
        return blueprint_value
    else:
        return random_generator.next_int()


def validate_number(value: Any) -> List[_types._ValidationFailure]:
    if isinstance(value, (int, float)) and not isinstance(value, (bool, str)):
        if isinstance(value, (int)):
            if (value > 2**63-1 or value < -(2**63)):
                return [_types._ValidationFailure([], "NumberOutOfRange", {})]
            else:
                return []
        else:
            return []
    else:
        return get_type_unexpected_validation_failure([], value, _NUMBER_NAME)


def generate_random_number(blueprint_value: Any, use_blueprint_value: bool,
                           random_generator: _rg._RandomGenerator) -> Any:
    if use_blueprint_value:
        return blueprint_value
    else:
        return random_generator.next_double()


def validate_string(value: Any) -> List[_types._ValidationFailure]:
    if isinstance(value, str):
        return []
    else:
        return get_type_unexpected_validation_failure([], value, _STRING_NAME)


def generate_random_string(blueprint_value: Any, use_blueprint_value: bool,
                           random_generator: _rg._RandomGenerator) -> str:
    if use_blueprint_value:
        return blueprint_value
    else:
        return random_generator.next_string()


def validate_array(value: Any, select: Dict[str, object], fn: str, type_parameters: List[_types._UTypeDeclaration],
                   generics: List[_types._UTypeDeclaration]) -> List[_types._ValidationFailure]:
    if isinstance(value, list):
        nested_type_declaration = type_parameters[0]
        validation_failures = []

        for i, element in enumerate(value):
            nested_validation_failures = nested_type_declaration.validate(
                element, select, fn, generics)
            index = i

            nested_validation_failures_with_path = [
                _types._ValidationFailure(
                    prepend(index, f.path), f.reason, f.data)
                for f in nested_validation_failures
            ]

            validation_failures.extend(nested_validation_failures_with_path)

        return validation_failures
    else:
        return get_type_unexpected_validation_failure([], value, _ARRAY_NAME)


def generate_random_array(blueprint_value: Any, use_blueprint_value: bool,
                          include_optional_fields: bool, randomize_optional_fields: bool, type_parameters: List[_types._UTypeDeclaration],
                          generics: List[_types._UTypeDeclaration], random_generator: _rg._RandomGenerator) -> List[Any]:
    nested_type_declaration = type_parameters[0]

    if use_blueprint_value:
        starting_array = blueprint_value
        array = [nested_type_declaration.generate_random_value(starting_array_value, True,
                                                               include_optional_fields, randomize_optional_fields, generics,
                                                               random_generator)
                 for starting_array_value in starting_array]
        return array
    else:
        length = random_generator.next_collection_length()
        array = [nested_type_declaration.generate_random_value(None, False, include_optional_fields, randomize_optional_fields,
                                                               generics, random_generator)
                 for _ in range(length)]
        return array


def validate_object(value: Any, select: Dict[str, object], fn: str, type_parameters: List[_types._UTypeDeclaration],
                    generics: List[_types._UTypeDeclaration]) -> List[_types._ValidationFailure]:
    if isinstance(value, dict):
        nested_type_declaration = type_parameters[0]

        validation_failures = []
        for k, v in value.items():
            nested_validation_failures = nested_type_declaration.validate(
                v, select, fn, generics)

            nested_validation_failures_with_path = []
            for f in nested_validation_failures:
                this_path = prepend(k, f.path)
                nested_validation_failures_with_path.append(
                    _types._ValidationFailure(this_path, f.reason, f.data))

            validation_failures.extend(nested_validation_failures_with_path)

        return validation_failures
    else:
        return get_type_unexpected_validation_failure([], value, _OBJECT_NAME)


def generate_random_object(blueprint_value: Any, use_blueprint_value: bool,
                           include_optional_fields: bool, randomize_optional_fields: bool, type_parameters: List[_types._UTypeDeclaration],
                           generics: List[_types._UTypeDeclaration], random_generator: _rg._RandomGenerator) -> Dict[str, Any]:
    nested_type_declaration = type_parameters[0]

    if use_blueprint_value:
        starting_obj = blueprint_value
        obj = {key: nested_type_declaration.generate_random_value(starting_obj_value, True,
                                                                  include_optional_fields, randomize_optional_fields, generics,
                                                                  random_generator)
               for key, starting_obj_value in starting_obj.items()}
        return obj
    else:
        length = random_generator.next_collection_length()
        obj = {random_generator.next_string(): nested_type_declaration.generate_random_value(None, False,
                                                                                             include_optional_fields, randomize_optional_fields,
                                                                                             generics, random_generator)
               for _ in range(length)}
        return obj


def validate_struct(value: Any, select: Dict[str, object], fn: str, type_parameters: List[_types._UTypeDeclaration],
                    generics: List[_types._UTypeDeclaration], fields: Dict[str, _types._UFieldDeclaration]) -> List[_types._ValidationFailure]:
    if isinstance(value, dict):
        return validate_struct_fields(fields, value, select, fn, type_parameters)
    else:
        return get_type_unexpected_validation_failure([], value, 'Object')


def validate_struct_fields(fields: Dict[str, _types._UFieldDeclaration],
                           actual_struct: Dict[str, Any], select: Dict[str, object], fn: str,
                           type_parameters: List[_types._UTypeDeclaration]) -> List[_types._ValidationFailure]:
    validation_failures: List[_types._ValidationFailure] = []

    missing_fields = [field_name for field_name, field_declaration in fields.items()
                      if field_name not in actual_struct and not field_declaration.optional]

    for missing_field in missing_fields:
        validation_failure = _types._ValidationFailure([missing_field],
                                                       "RequiredObjectKeyMissing",
                                                       {})
        validation_failures.append(validation_failure)

    for field_name, field_value in actual_struct.items():
        reference_field = fields.get(field_name)
        if reference_field is None:
            validation_failure = _types._ValidationFailure(
                [field_name], "ObjectKeyDisallowed", {})
            validation_failures.append(validation_failure)
            continue

        ref_field_type_declaration = reference_field.type_declaration

        nested_validation_failures = ref_field_type_declaration.validate(
            field_value, select, fn, type_parameters)

        for failure in nested_validation_failures:
            this_path = [field_name] + failure.path
            nested_validation_failures_with_path = _types._ValidationFailure(
                this_path, failure.reason, failure.data)
            validation_failures.append(nested_validation_failures_with_path)

    return validation_failures


def generate_random_struct(blueprint_value: Any, use_blueprint_value: bool,
                           include_optional_fields: bool, randomize_optional_fields: bool, type_parameters: List[_types._UTypeDeclaration],
                           generics: List[_types._UTypeDeclaration], random_generator: _rg._RandomGenerator,
                           fields: Dict[str, _types._UFieldDeclaration]) -> Dict[str, Any]:
    if use_blueprint_value:
        starting_struct_value = blueprint_value
        return construct_random_struct(fields, starting_struct_value, include_optional_fields, randomize_optional_fields,
                                       type_parameters, random_generator)
    else:
        return construct_random_struct(fields, {}, include_optional_fields, randomize_optional_fields,
                                       type_parameters, random_generator)


def construct_random_struct(reference_struct: Dict[str, _types._UFieldDeclaration], starting_struct: Dict[str, Any],
                            include_optional_fields: bool, randomize_optional_fields: bool, type_parameters: List[_types._UTypeDeclaration],
                            random_generator: _rg._RandomGenerator) -> Dict[str, Any]:
    sorted_reference_struct = sorted(
        reference_struct.items(), key=lambda x: x[0])

    obj = OrderedDict()
    for field_name, field_declaration in sorted_reference_struct:
        blueprint_value = starting_struct.get(field_name)
        use_blueprint_value = field_name in starting_struct
        type_declaration: _types._UTypeDeclaration = field_declaration.type_declaration

        if use_blueprint_value:
            value = type_declaration.generate_random_value(blueprint_value, use_blueprint_value,
                                                           include_optional_fields, randomize_optional_fields, type_parameters,
                                                           random_generator)
        else:
            if not field_declaration.optional:
                value = type_declaration.generate_random_value(None, False,
                                                               include_optional_fields, randomize_optional_fields, type_parameters,
                                                               random_generator)
            else:
                if not include_optional_fields or (randomize_optional_fields and random_generator.next_boolean()):
                    continue

                value = type_declaration.generate_random_value(None, False,
                                                               include_optional_fields, randomize_optional_fields, type_parameters,
                                                               random_generator)

        obj[field_name] = value

    return obj


def union_entry(union: Dict[str, Any]) -> Tuple[str, Any]:
    return next(iter(union.items()), None)


def validate_union(value: Any, select: Dict[str, object], fn: str,
                   type_parameters: List[_types._UTypeDeclaration],
                   generics: List[_types._UTypeDeclaration],
                   cases: Dict[str, _types._UStruct]) -> List[_types._ValidationFailure]:
    if isinstance(value, dict):
        return validate_union_cases(cases, value, select, fn, type_parameters)
    else:
        return get_type_unexpected_validation_failure([], value, _UNION_NAME)


def validate_union_cases(reference_cases: Dict[str, _types._UStruct],
                         actual: Dict[str, Any], select: Dict[str, object], fn: str,
                         type_parameters: List[_types._UTypeDeclaration]) -> List[_types._ValidationFailure]:
    if len(actual) != 1:
        return [_types._ValidationFailure([],
                                          "ObjectSizeUnexpected",
                                          {"actual": len(actual), "expected": 1})]

    union_target, union_payload = union_entry(actual)

    reference_struct = reference_cases.get(union_target)
    if reference_struct is None:
        return [_types._ValidationFailure([union_target], "ObjectKeyDisallowed", {})]

    if isinstance(union_payload, dict):
        nested_validation_failures = validate_union_struct(
            reference_struct, union_target, union_payload, select, fn, type_parameters)

        nested_validation_failures_with_path = []
        for failure in nested_validation_failures:
            this_path = [union_target] + failure.path
            nested_validation_failures_with_path.append(
                _types._ValidationFailure(this_path, failure.reason, failure.data))

        return nested_validation_failures_with_path
    else:
        return get_type_unexpected_validation_failure([union_target], union_payload, "Object")


def validate_union_struct(union_struct: _types._UStruct,
                          union_case: str,
                          actual: Dict[str, Any], select: Dict[str, object], fn: str,
                          type_parameters: List[_types._UTypeDeclaration]) -> List[_types._ValidationFailure]:
    return validate_struct_fields(union_struct.fields, actual, select, fn, type_parameters)


def generate_random_union(blueprint_value: Any, use_blueprint_value: bool,
                          include_optional_fields: bool, randomize_optional_fields: bool,
                          type_parameters: List[Any],
                          generics: List[_types._UTypeDeclaration],
                          random_generator: _rg._RandomGenerator,
                          cases: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if use_blueprint_value:
        starting_union_case = blueprint_value
        return construct_random_union(cases, starting_union_case, include_optional_fields, randomize_optional_fields,
                                      type_parameters, random_generator)
    else:
        return construct_random_union(cases, {}, include_optional_fields, randomize_optional_fields,
                                      type_parameters, random_generator)


def construct_random_union(union_cases_reference: Dict[str, Dict[str, Any]],
                           starting_union: Dict[str, Any],
                           include_optional_fields: bool, randomize_optional_fields: bool,
                           type_parameters: List[Any],
                           random_generator: _rg._RandomGenerator) -> Dict[str, Any]:
    if starting_union:
        union_case, union_starting_struct = union_entry(starting_union)
        union_struct_type: _types._UStruct = union_cases_reference[union_case]
        return {union_case: construct_random_struct(union_struct_type.fields, union_starting_struct,
                                                    include_optional_fields, randomize_optional_fields, type_parameters,
                                                    random_generator)}
    else:
        sorted_union_cases_reference = sorted(
            union_cases_reference.items(), key=lambda x: x[0])
        random_index = random_generator.next_int_with_ceiling(
            len(sorted_union_cases_reference) - 1)
        union_case, union_data = sorted_union_cases_reference[random_index]
        return {union_case: construct_random_struct(union_data.fields, {},
                                                    include_optional_fields, randomize_optional_fields, type_parameters,
                                                    random_generator)}


def generate_random_fn(blueprint_value: Any,
                       use_blueprint_value: bool,
                       include_optional_fields: bool, randomize_optional_fields: bool,
                       type_parameters: List[_types._UTypeDeclaration],
                       generics: List[_types._UTypeDeclaration],
                       random: _rg._RandomGenerator,
                       call_cases: Dict[str, _types._UStruct]) -> Dict[str, Any]:
    if use_blueprint_value:
        starting_fn_value = blueprint_value
    else:
        starting_fn_value = {}

    return generate_random_union(starting_fn_value,
                                 use_blueprint_value,
                                 include_optional_fields, randomize_optional_fields,
                                 type_parameters,
                                 generics,
                                 random,
                                 call_cases)


def validate_select(given_obj: Any, select: Dict[str, object], fn: str, type_parameters: List['_types._UTypeDeclaration'],
                       generics: List['_types._UTypeDeclaration'], types: Dict[str, '_types._UType']) -> List['_types._ValidationFailure']:
    if not isinstance(given_obj, dict):
        return get_type_unexpected_validation_failure([], given_obj, "Object")

    select_struct_fields_header = given_obj

    validation_failures: List[_types._ValidationFailure] = []
    function_type: _types._UFn = types[fn]

    for type_name, select_value in select_struct_fields_header.items():
        type_reference = function_type.result if type_name == "->" else types.get(
            type_name)

        if type_reference is None:
            validation_failures.append(_types._ValidationFailure(
                [type_name], "ObjectKeyDisallowed", {}))
            continue

        if isinstance(type_reference, _types._UUnion):
            if not isinstance(select_value, dict):
                validation_failures.extend(get_type_unexpected_validation_failure(
                    [type_name], select_value, "Object"))
                continue

            union_cases = select_value

            for union_case, selected_case_struct_fields in union_cases.items():
                struct_ref = type_reference.cases.get(union_case)
                loop_path = [type_name, union_case]

                if struct_ref is None:
                    validation_failures.append(_types._ValidationFailure(
                        loop_path, "ObjectKeyDisallowed", {}))
                    continue

                nested_validation_failures = validate_select_struct(
                    struct_ref, loop_path, selected_case_struct_fields)
                validation_failures.extend(nested_validation_failures)
        elif isinstance(type_reference, _types._UFn):
            fn_call = type_reference.call
            fn_call_cases = fn_call.cases
            fn_name = type_reference.name
            arg_struct = fn_call_cases.get(fn_name)
            nested_validation_failures = validate_select_struct(
                arg_struct, [type_name], select_value)
            validation_failures.extend(nested_validation_failures)
        else:
            struct_ref = type_reference
            nested_validation_failures = validate_select_struct(
                struct_ref, [type_name], select_value)
            validation_failures.extend(nested_validation_failures)

    return validation_failures


def validate_select_struct(struct_reference: _types._UStruct, base_path: List[Any], selected_fields: Any) -> List[_types._ValidationFailure]:
    validation_failures: List[_types._ValidationFailure] = []

    if not isinstance(selected_fields, list):
        return get_type_unexpected_validation_failure(base_path, selected_fields, "Array")

    fields = selected_fields

    for i, field in enumerate(fields):
        if not isinstance(field, str):
            this_path = base_path + [i]
            validation_failures.extend(
                get_type_unexpected_validation_failure(this_path, field, "String"))
            continue
        string_field = field
        if string_field not in struct_reference.fields:
            this_path = base_path + [i]
            validation_failures.append(_types._ValidationFailure(
                this_path, "ObjectKeyDisallowed", {}))

    return validation_failures


def validate_mock_call(given_obj: Any, select: Dict[str, object], fn: str, type_parameters: List['_types._UTypeDeclaration'],
                       generics: List['_types._UTypeDeclaration'], types: Dict[str, '_types._UType']) -> List['_types._ValidationFailure']:
    try:
        given_map = as_map(given_obj)
    except TypeError:
        return get_type_unexpected_validation_failure([], given_obj, "Object")

    regex_string = "^fn\\..*$"

    matches = [k for k in given_map.keys() if re.match(regex_string, k)]
    if len(matches) != 1:
        return [_types._ValidationFailure([], "ObjectKeyRegexMatchCountUnexpected",
                                          {"regex": regex_string, "actual": len(matches), "expected": 1})]

    function_name = matches[0]
    function_def = types[function_name]
    input_value = given_map[function_name]

    function_def_call = function_def.call
    function_def_name = function_def.name
    function_def_call_cases = function_def_call.cases

    input_failures = function_def_call_cases[function_def_name].validate(
        input_value, select, fn, [], [])

    input_failures_with_path = []
    for f in input_failures:
        new_path = [function_name] + f.path
        input_failures_with_path.append(
            _types._ValidationFailure(new_path, f.reason, f.data))

    return [f for f in input_failures_with_path if f.reason != "RequiredObjectKeyMissing"]


def validate_mock_stub(given_obj: Any, select: Dict[str, object], fn: str, type_parameters: List['_types._UTypeDeclaration'],
                       generics: List['_types._UTypeDeclaration'], types: Dict[str, '_types._UType']) -> List['_types._ValidationFailure']:
    validation_failures = []

    try:
        given_map = as_map(given_obj)
    except TypeError:
        return get_type_unexpected_validation_failure([], given_obj, "Object")

    regex_string = "^fn\\..*$"

    matches = [k for k in given_map.keys() if re.match(regex_string, k)]
    if len(matches) != 1:
        return [_types._ValidationFailure([], "ObjectKeyRegexMatchCountUnexpected",
                                          {"regex": regex_string, "actual": len(matches), "expected": 1})]

    function_name = matches[0]
    function_def = types[function_name]
    input_value = given_map[function_name]

    function_def_call = function_def.call
    function_def_name = function_def.name
    function_def_call_cases = function_def_call.cases

    input_failures = function_def_call_cases[function_def_name].validate(
        input_value, select, fn, [], [])

    input_failures_with_path = []
    for f in input_failures:
        this_path = [function_name] + f.path
        input_failures_with_path.append(
            _types._ValidationFailure(this_path, f.reason, f.data))

    input_failures_without_missing_required = [
        f for f in input_failures_with_path if f.reason != "RequiredObjectKeyMissing"]
    validation_failures.extend(input_failures_without_missing_required)

    result_def_key = "->"

    if result_def_key not in given_map:
        validation_failures.append(_types._ValidationFailure(
            [result_def_key], "RequiredObjectKeyMissing", {}))
    else:
        output = given_map[result_def_key]
        output_failures = function_def.result.validate(output, select, fn, [], [])

        output_failures_with_path = []
        for f in output_failures:
            this_path = [result_def_key] + f.path
            output_failures_with_path.append(
                _types._ValidationFailure(this_path, f.reason, f.data))

        failures_without_missing_required = [
            f for f in output_failures_with_path if f.reason != "RequiredObjectKeyMissing"]
        validation_failures.extend(failures_without_missing_required)

    disallowed_fields = [k for k in given_map.keys(
    ) if k not in matches and k != result_def_key]
    for disallowed_field in disallowed_fields:
        validation_failures.append(_types._ValidationFailure(
            [disallowed_field], "ObjectKeyDisallowed", {}))

    return validation_failures


def select_struct_fields(type_declaration: '_types._UTypeDeclaration', value: Any,
                         selected_struct_fields: Dict[str, Any]) -> Any:
    type_declaration_type = type_declaration.type
    type_declaration_type_params = type_declaration.type_parameters

    if isinstance(type_declaration_type, _types._UStruct):
        fields = type_declaration_type.fields
        struct_name = type_declaration_type.name
        selected_fields = selected_struct_fields.get(struct_name, None)
        value_as_map = value

        final_map = {}
        for entry_key, entry_value in value_as_map.items():
            if selected_fields is None or entry_key in selected_fields:
                field = fields[entry_key]
                field_type_declaration = field.type_declaration
                value_with_selected_fields = select_struct_fields(
                    field_type_declaration, entry_value, selected_struct_fields)

                final_map[entry_key] = value_with_selected_fields

        return final_map

    elif isinstance(type_declaration_type, _types._UFn):
        value_as_map = value
        u_entry = union_entry(value_as_map)
        union_case = u_entry[0]
        union_data = u_entry[1]

        fn_name = type_declaration_type.name
        fn_call = type_declaration_type.call
        fn_call_cases = fn_call.cases

        arg_struct_reference = fn_call_cases[union_case]
        selected_fields = selected_struct_fields.get(fn_name, None)

        final_map = {}
        for entry_key, entry_value in union_data.items():
            if selected_fields is None or entry_key in selected_fields:
                field = arg_struct_reference.fields[entry_key]
                value_with_selected_fields = select_struct_fields(
                    field.type_declaration, entry_value, selected_struct_fields)

                final_map[entry_key] = value_with_selected_fields

        return {union_case: final_map}

    elif isinstance(type_declaration_type, _types._UUnion):
        value_as_map = value
        u_entry = union_entry(value_as_map)
        union_case = u_entry[0]
        union_data = u_entry[1]

        union_cases = type_declaration_type.cases
        union_struct_reference = union_cases[union_case]
        union_struct_ref_fields = union_struct_reference.fields
        default_cases_to_fields = {}

        for case_key, case_value in union_cases.items():
            union_struct = case_value
            union_struct_fields = union_struct.fields
            fields = list(union_struct_fields.keys())
            default_cases_to_fields[case_key] = fields

        union_selected_fields = selected_struct_fields.get(
            type_declaration_type.name, default_cases_to_fields)
        this_union_case_selected_fields_default = default_cases_to_fields.get(
            union_case, None)
        selected_fields = union_selected_fields.get(
            union_case, this_union_case_selected_fields_default)

        final_map = {}
        for entry_key, entry_value in union_data.items():
            if selected_fields is None or entry_key in selected_fields:
                field = union_struct_ref_fields[entry_key]
                value_with_selected_fields = select_struct_fields(
                    field.type_declaration, entry_value, selected_struct_fields)
                final_map[entry_key] = value_with_selected_fields

        return {union_case: final_map}

    elif isinstance(type_declaration_type, _types._UObject):
        nested_type_declaration = type_declaration_type_params[0]
        value_as_map = value

        final_map = {}
        for entry_key, entry_value in value_as_map.items():
            value_with_selected_fields = select_struct_fields(
                nested_type_declaration, entry_value, selected_struct_fields)
            final_map[entry_key] = value_with_selected_fields

        return final_map

    elif isinstance(type_declaration_type, _types._UArray):
        nested_type = type_declaration_type_params[0]
        value_as_list = value

        final_list = []
        for entry in value_as_list:
            value_with_selected_fields = select_struct_fields(
                nested_type, entry, selected_struct_fields)
            final_list.append(value_with_selected_fields)

        return final_list

    else:
        return value


def get_invalid_error_message(error: str, validation_failures: List[_types._ValidationFailure],
                              result_union_type: _types._UUnion, response_headers: Dict[str, Any]) -> 'types.Message':
    validation_failure_cases = map_validation_failures_to_invalid_field_cases(
        validation_failures)
    new_error_result = {error: {"cases": validation_failure_cases}}

    validate_result(result_union_type, new_error_result)
    return types.Message(response_headers, new_error_result)


def map_validation_failures_to_invalid_field_cases(argument_validation_failures: List[_types._ValidationFailure]) -> List[Dict[str, Any]]:
    validation_failure_cases = []
    for validation_failure in argument_validation_failures:
        validation_failure_case = {"path": validation_failure.path,
                                   "reason": {validation_failure.reason: validation_failure.data}}
        validation_failure_cases.append(validation_failure_case)

    return validation_failure_cases


def validate_result(result_union_type: _types._UUnion, error_result: Any) -> None:
    new_error_result_validation_failures = result_union_type.validate(
        error_result, None, None, [], [])
    if new_error_result_validation_failures:
        raise types.UApiError("Failed internal uAPI validation: " +
                              str(map_validation_failures_to_invalid_field_cases(new_error_result_validation_failures)))


async def handle_message(request_message: 'types.Message', u_api_schema: 'types.UApiSchema',
                         handler: Callable[['types.Message'], Coroutine[Any, Any, 'types.Message']],
                         on_error: Callable[[Exception], None]) -> 'types.Message':
    response_headers: Dict[str, Any] = {}
    request_headers: Dict[str, Any] = request_message.header
    request_body: Dict[str, Any] = request_message.body
    parsed_u_api_schema: Dict[str, Any] = u_api_schema.parsed
    request_entry: Tuple[str, Any] = union_entry(request_body)

    request_target_init: str = request_entry[0]
    request_payload: Dict[str, Any] = request_entry[1]

    unknown_target: Optional[str]
    request_target: str
    if request_target_init not in parsed_u_api_schema:
        unknown_target = request_target_init
        request_target = "fn._unknown"
    else:
        unknown_target = None
        request_target = request_target_init

    function_type: _types._UFn = parsed_u_api_schema[request_target]
    result_union_type: _types._UUnion = function_type.result

    call_id: Any = request_headers.get('_id')
    if call_id is not None:
        response_headers['_id'] = call_id

    if '_parseFailures' in request_headers:
        parse_failures: List[Any] = request_headers['_parseFailures']
        new_error_result: Dict[str, Any] = {
            '_ErrorParseFailure': {'reasons': parse_failures}}

        validate_result(result_union_type, new_error_result)

        return types.Message(response_headers, new_error_result)

    header_validation_failures: List[Any] = validate_headers(
        request_headers, u_api_schema, function_type)
    if header_validation_failures:
        return get_invalid_error_message('_ErrorInvalidRequestHeaders', header_validation_failures, result_union_type, response_headers)

    if '_bin' in request_headers:
        client_known_binary_checksums: List[Any] = request_headers['_bin']

        response_headers['_binary'] = True
        response_headers['_clientKnownBinaryChecksums'] = client_known_binary_checksums

        if '_pac' in request_headers:
            response_headers['_pac'] = request_headers['_pac']

    select_struct_fields_header: Dict[str, object] = request_headers.get('_sel', None)

    if unknown_target:
        new_error_result: Dict[str, Any] = {'_ErrorInvalidRequestBody': {
            'cases': [{'path': [unknown_target], 'reason': {'FunctionUnknown': {}}}]}}
        validate_result(result_union_type, new_error_result)
        return types.Message(response_headers, new_error_result)

    function_type_call: _types._UUnion = function_type.call

    call_validation_failures: List[Any] = function_type_call.validate(
        request_body, None, None, [], [])
    if call_validation_failures:
        return get_invalid_error_message('_ErrorInvalidRequestBody', call_validation_failures, result_union_type, response_headers)

    unsafe_response_enabled: bool = request_headers.get('_unsafe') == True

    call_message: types.Message = types.Message(
        request_headers, {request_target: request_payload})

    if request_target == 'fn._ping':
        result_message: types.Message = types.Message({}, {'Ok': {}})
    elif request_target == 'fn._api':
        result_message = types.Message(
            {}, {'Ok': {'api': u_api_schema.original}})
    else:
        try:
            result_message = await handler(call_message)
        except Exception as e:
            try:
                on_error(e)
            except Exception:
                pass
            return types.Message(response_headers, {'_ErrorUnknown': {}})

    skip_result_validation: bool = unsafe_response_enabled
    if not skip_result_validation:
        result_validation_failures: List[Any] = result_union_type.validate(
            result_message.body, select_struct_fields_header, None, [], [])
        if result_validation_failures:
            return get_invalid_error_message('_ErrorInvalidResponseBody', result_validation_failures, result_union_type, response_headers)

    result_union: Dict[str, Any] = result_message.body

    result_message.header.update(response_headers)
    final_response_headers: Dict[str, Any] = result_message.header

    final_result_union: Dict[str, Any]
    if select_struct_fields_header:
        select_struct_fields_header: Dict[str, Any] = request_headers['_sel']
        final_result_union = select_struct_fields(_types._UTypeDeclaration(
            result_union_type, False, []), result_union, select_struct_fields_header)
    else:
        final_result_union = result_union

    return types.Message(final_response_headers, final_result_union)


def parse_request_message(request_message_bytes: bytes, serializer: 'types.Serializer', uapi_schema: 'types.UApiSchema',
                          on_error: Callable[[Exception], None]) -> 'types.Message':
    try:
        return serializer.deserialize(request_message_bytes)
    except Exception as e:
        on_error(e)

        error_reason = {
            _types._BinaryEncoderUnavailableError: "IncompatibleBinaryEncoding",
            _types._BinaryEncodingMissing: "BinaryDecodeFailure",
            _types._InvalidMessage: "ExpectedJsonArrayOfTwoObjects",
            _types._InvalidMessageBody: "ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject"
        }.get(type(e), "ExpectedJsonArrayOfTwoObjects")

        return types.Message({"_parseFailures": [{error_reason: {}}]}, {"_unknown": {}})


async def process_bytes(request_message_bytes: bytes, serializer: 'types.Serializer', uapi_schema: 'types.UApiSchema',
                        on_error: Callable[[Exception], None], on_request: Callable[['types.Message'], None],
                        on_response: Callable[['types.Message'], None], handler: Callable[['types.Message'], Coroutine[Any, Any, 'types.Message']]) -> bytes:
    try:
        request_message = parse_request_message(
            request_message_bytes, serializer, uapi_schema, on_error)

        try:
            on_request(request_message)
        except Exception:
            pass

        response_message = await handle_message(
            request_message, uapi_schema, handler, on_error)

        try:
            on_response(response_message)
        except Exception:
            pass

        return serializer.serialize(response_message)
    except Exception as e:
        try:
            on_error(e)
        except Exception:
            pass

        return serializer.serialize(types.Message({}, {"_ErrorUnknown": {}}))


def is_sub_map(part: Dict[str, Any], whole: Dict[str, Any]) -> bool:
    for part_key, part_value in part.items():
        whole_value = whole.get(part_key)
        if not is_sub_map_entry_equal(part_value, whole_value):
            return False
    return True


def is_sub_map_entry_equal(part_value: Any, whole_value: Any) -> bool:
    if isinstance(part_value, dict) and isinstance(whole_value, dict):
        return is_sub_map(part_value, whole_value)
    elif isinstance(part_value, list) and isinstance(whole_value, list):
        for part_element in part_value:
            if any(is_sub_map_entry_equal(part_element, whole_element) for whole_element in whole_value):
                return True
        return False
    else:
        return part_value == whole_value


def verify(function_name: str, argument: Dict[str, Any], exact_match: bool,
           verification_times: Dict[str, Any], invocations: List[_types._MockInvocation]) -> Dict[str, Any]:
    matches_found = 0
    for invocation in invocations:
        if invocation.function_name == function_name:
            if exact_match:
                if invocation.function_argument == argument:
                    invocation.verified = True
                    matches_found += 1
            elif is_sub_map(argument, invocation.function_argument):
                invocation.verified = True
                matches_found += 1

    all_calls_pseudo_json = [
        {invocation.function_name: invocation.function_argument} for invocation in invocations]

    verify_times_entry = next(iter(verification_times.items()))
    verify_key, verify_times_struct = verify_times_entry

    verification_failure_pseudo_json = None
    if verify_key == "Exact":
        times = verify_times_struct["times"]
        if matches_found > times:
            verification_failure_pseudo_json = {
                "TooManyMatchingCalls": {
                    "wanted": {"Exact": {"times": times}},
                    "found": matches_found,
                    "allCalls": all_calls_pseudo_json
                }
            }
        elif matches_found < times:
            verification_failure_pseudo_json = {
                "TooFewMatchingCalls": {
                    "wanted": {"Exact": {"times": times}},
                    "found": matches_found,
                    "allCalls": all_calls_pseudo_json
                }
            }
    elif verify_key == "AtMost":
        times = verify_times_struct["times"]
        if matches_found > times:
            verification_failure_pseudo_json = {
                "TooManyMatchingCalls": {
                    "wanted": {"AtMost": {"times": times}},
                    "found": matches_found,
                    "allCalls": all_calls_pseudo_json
                }
            }
    elif verify_key == "AtLeast":
        times = verify_times_struct["times"]
        if matches_found < times:
            verification_failure_pseudo_json = {
                "TooFewMatchingCalls": {
                    "wanted": {"AtLeast": {"times": times}},
                    "found": matches_found,
                    "allCalls": all_calls_pseudo_json
                }
            }

    if verification_failure_pseudo_json is None:
        return {"Ok": {}}

    return {"ErrorVerificationFailure": {"reason": verification_failure_pseudo_json}}


def verify_no_more_interactions(invocations: List[_types._MockInvocation]) -> Dict[str, Any]:
    invocations_not_verified = [
        invocation for invocation in invocations if not invocation.verified]

    if invocations_not_verified:
        unverified_calls_pseudo_json = [{invocation.function_name: invocation.function_argument}
                                        for invocation in invocations_not_verified]
        return {"ErrorVerificationFailure": {"additionalUnverifiedCalls": unverified_calls_pseudo_json}}

    return {"Ok": {}}


async def mock_handle(request_message: 'types.Message', stubs: List[_types._MockStub], invocations: List[_types._MockInvocation],
                      random: _rg._RandomGenerator, u_api_schema: 'types.UApiSchema', enable_generated_default_stub: bool, 
                      enable_optional_field_generation: bool, randomize_optional_field_generation: bool) -> 'types.Message':
    header: Dict[str, Any] = request_message.header

    enable_generation_stub: bool = header.get(
        "_gen", False)
    function_name: str = request_message.get_body_target()
    argument: Dict[str, Any] = request_message.get_body_payload()

    if function_name == "fn._createStub":
        given_stub: Dict[str, Any] = argument["stub"]

        stub_call_key, stub_call_value = next(
            (k, v) for k, v in given_stub.items() if k.startswith("fn."))
        stub_function_name: str = stub_call_key
        stub_arg: Dict[str, Any] = stub_call_value
        stub_result: Dict[str, Any] = given_stub["->"]
        allow_argument_partial_match: bool = not argument.get(
            "strictMatch!", False)
        stub_count: int = argument.get("count!", -1)

        stub = _types._MockStub(stub_function_name, stub_arg, stub_result,
                                allow_argument_partial_match, stub_count)

        stubs.insert(0, stub)
        return types.Message({}, {"Ok": {}})

    elif function_name == "fn._verify":
        given_call: Dict[str, Any] = argument["call"]

        call_key, call_value = next(
            (k, v) for k, v in given_call.items() if k.startswith("fn."))
        call_function_name: str = call_key
        call_arg: Dict[str, Any] = call_value
        verify_times: Dict[str, Any] = argument.get(
            "count!", {"AtLeast": {"times": 1}})
        strict_match: bool = argument.get("strictMatch!", False)

        verification_result = verify(call_function_name, call_arg, strict_match,
                                     verify_times,
                                     invocations)
        return types.Message({}, verification_result)

    elif function_name == "fn._verifyNoMoreInteractions":
        verification_result = verify_no_more_interactions(invocations)
        return types.Message({}, verification_result)

    elif function_name == "fn._clearCalls":
        invocations.clear()
        return types.Message({}, {"Ok": {}})

    elif function_name == "fn._clearStubs":
        stubs.clear()
        return types.Message({}, {"Ok": {}})

    elif function_name == "fn._setRandomSeed":
        given_seed: int = argument["seed"]

        random.set_seed(given_seed)
        return types.Message({}, {"Ok": {}})

    else:
        invocations.append(_types._MockInvocation(
            function_name, argument))

        definition: _types._UFn = u_api_schema.parsed.get(function_name)

        for stub in stubs:
            if stub.count == 0:
                continue
            if stub.when_function == function_name:
                if stub.allow_argument_partial_match:
                    if is_sub_map(stub.when_argument, argument):
                        use_blueprint_value = True
                        include_optional_fields = False
                        result = definition.result.generate_random_value(
                            stub.then_result, use_blueprint_value,
                            include_optional_fields, randomize_optional_field_generation, [], [], random)
                        if stub.count > 0:
                            stub.count -= 1
                        return types.Message({}, result)
                else:
                    if stub.when_argument == argument:
                        use_blueprint_value = True
                        include_optional_fields = False
                        result = definition.result.generate_random_value(
                            stub.then_result, use_blueprint_value,
                            include_optional_fields, randomize_optional_field_generation, [], [], random)
                        if stub.count > 0:
                            stub.count -= 1
                        return types.Message({}, result)

        if not enable_generated_default_stub and not enable_generation_stub:
            return types.Message({}, {"_ErrorNoMatchingStub": {}})

        if definition is not None:
            result_union = definition.result
            ok_struct_ref = result_union.cases["Ok"]
            use_blueprint_value = True
            include_optional_fields = True
            random_ok_struct = ok_struct_ref.generate_random_value({}, use_blueprint_value,
                                                                   include_optional_fields, randomize_optional_field_generation, 
                                                                   [], [], random)
            return types.Message({}, {"Ok": random_ok_struct})
        else:
            raise types.UApiError(
                "Unexpected unknown function: %s" % function_name)


async def process_request_object(request_message: 'types.Message',
                                 adapter: Callable[['types.Message', 'types.Serializer'], Coroutine[Any, Any, 'types.Message']], serializer: 'types.Serializer',
                                 timeout_ms_default: int, use_binary_default: bool) -> 'types.Message':
    header: Dict[str, Any] = request_message.header

    try:
        if "_tim" not in header:
            header["_tim"] = timeout_ms_default

        if use_binary_default:
            header["_binary"] = True

        timeout_ms: int = header.get("_tim")

        async with asyncio.timeout(timeout_ms / 1000):
            response_message = await adapter(request_message, serializer)

        if response_message.body == {"_ErrorParseFailure": {"reasons": [{"IncompatibleBinaryEncoding": {}}]}}:
            header["_binary"] = True
            header["_forceSendJson"] = True

            async with asyncio.timeout(timeout_ms / 1000):
                return await adapter(request_message, serializer)

        return response_message
    except Exception as e:
        raise types.UApiError(e)


def map_schema_parse_failures_to_pseudo_json(schema_parse_failures: List[_types._SchemaParseFailure]) -> List[Dict[str, Any]]:
    """
    Map schema parse failures to pseudo JSON format.
    """
    return [{'path': f.path, 'reason': {f.reason: f.data}} for f in schema_parse_failures]
