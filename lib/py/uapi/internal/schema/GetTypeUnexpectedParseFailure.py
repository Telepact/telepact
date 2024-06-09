from typing import list, object, dict

from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure


def get_type_unexpected_parse_failure(path: list[object], value: object, expected_type: str) -> list[SchemaParseFailure]:
    from uapi.internal.types.GetType import get_type

    actual_type = get_type(value)
    data = {
        "actual": {actual_type: {}},
        "expected": {expected_type: {}}
    }
    return [
        SchemaParseFailure(path, "TypeUnexpected", data, None)
    ]
