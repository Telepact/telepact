from typing import List, Any, Dict
from uapi.internal.types import get_type
from uapi.internal.schema import SchemaParseFailure


def get_type_unexpected_parse_failure(path: List[Any], value: Any, expected_type: str) -> List[SchemaParseFailure]:
    actual_type = get_type(value)
    data = {
        "actual": {actual_type: {}},
        "expected": {expected_type: {}}
    }
    return [
        SchemaParseFailure(path, "TypeUnexpected", data, None)
    ]
