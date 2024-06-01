from typing import List, Dict, Any, Set
from uapi.internal.types import UFieldDeclaration, UStruct, UType, UUnion
from uapi import UApiSchemaParseError


def parse_union_type(path: List[Any], union_definition_as_pseudo_json: Dict[str, Any], schema_key: str,
                     ignore_keys: List[str], required_keys: List[str], type_parameter_count: int,
                     u_api_schema_pseudo_json: List[Any], schema_keys_to_index: Dict[str, int],
                     parsed_types: Dict[str, UType], type_extensions: Dict[str, UType],
                     all_parse_failures: List[SchemaParseFailure], failed_types: Set[str]) -> UUnion:
    parse_failures = []

    other_keys = set(union_definition_as_pseudo_json.keys())
    other_keys.remove(schema_key)
    other_keys.remove("///")
    for ignore_key in ignore_keys:
        other_keys.remove(ignore_key)

    if other_keys:
        for k in other_keys:
            loop_path = path + [k]
            parse_failures.append(SchemaParseFailure(
                loop_path, "ObjectKeyDisallowed", {}, None))

    this_path = path + [schema_key]
    def_init = union_definition_as_pseudo_json[schema_key]

    if not isinstance(def_init, list):
        final_parse_failures = get_type_unexpected_parse_failure(
            this_path, def_init, "Array")
        parse_failures.extend(final_parse_failures)
        raise UApiSchemaParseError(parse_failures)

    definition2 = def_init
    definition = []
    index = -1
    for element in definition2:
        index += 1
        loop_path = this_path + [index]
        if not isinstance(element, dict):
            this_parse_failures = get_type_unexpected_parse_failure(
                loop_path, element, "Object")
            parse_failures.extend(this_parse_failures)
            continue
        definition.append(element)

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    if not definition and not required_keys:
        parse_failures.append(SchemaParseFailure(
            this_path, "EmptyArrayDisallowed", {}, None))
    else:
        for required_key in required_keys:
            for element in definition:
                keys = set(element.keys())
                keys.remove("///")
                if required_key in keys:
                    break
            else:
                branch_path = this_path + [0, required_key]
                parse_failures.append(SchemaParseFailure(
                    branch_path, "RequiredObjectKeyMissing", {}, None))

    cases = {}
    case_indices = {}

    for i, element in enumerate(definition):
        loop_path = this_path + [i]
        map_init = element
        map = dict(map_init)
        map.pop("///", None)
        keys = list(map.keys())

        regex_string = r"^([A-Z][a-zA-Z0-9_]*)$"

        matches = [k for k in keys if re.match(regex_string, k)]
        if len(matches) != 1:
            parse_failures.append(SchemaParseFailure(loop_path, "ObjectKeyRegexMatchCountUnexpected",
                                                     {"regex": regex_string, "actual": len(matches),
                                                      "expected": 1, "keys": keys}, None))
            continue
        if len(map) != 1:
            parse_failures.append(SchemaParseFailure(loop_path, "ObjectSizeUnexpected",
                                                     {"expected": 1, "actual": len(map)}, None))
            continue

        entry = next(iter(map.items()))
        union_case = entry[0]
        union_key_path = loop_path + [union_case]

        if not isinstance(entry[1], dict):
            this_parse_failures = get_type_unexpected_parse_failure(
                union_key_path, entry[1], "Object")
            parse_failures.extend(this_parse_failures)
            continue
        union_case_struct = entry[1]

        try:
            fields = parse_struct_fields(union_case_struct, union_key_path, type_parameter_count,
                                         u_api_schema_pseudo_json, schema_keys_to_index, parsed_types,
                                         type_extensions, all_parse_failures, failed_types)
        except UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)
            continue

        union_struct = UStruct(
            f"{schema_key}.{union_case}", fields, type_parameter_count)

        cases[union_case] = union_struct
        case_indices[union_case] = i

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    return UUnion(schema_key, cases, case_indices, type_parameter_count)
