from typing import List, Any, Dict

from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure


def get_type_unexpected_parse_failure(path: List[Any], value: Any, expected_type: str) -> List[SchemaParseFailure]:
    from uapi.internal.types.GetType import get_type

    actual_type = get_type(value)
    data = {
        "actual": {actual_type: {}},
        "expected": {expected_type: {}}
    }
    return [
        SchemaParseFailure(path, "TypeUnexpected", data, None)
    ]
