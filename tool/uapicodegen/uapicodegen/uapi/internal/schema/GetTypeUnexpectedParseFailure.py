from ...internal.schema.SchemaParseFailure import SchemaParseFailure


def get_type_unexpected_parse_failure(document_name: str, path: list[object], value: object, expected_type: str) -> list[SchemaParseFailure]:
    from ...internal.types.GetType import get_type

    actual_type = get_type(value)
    data: dict[str, object] = {
        "actual": {actual_type: {}},
        "expected": {expected_type: {}}
    }
    return [
        SchemaParseFailure(document_name, path, "TypeUnexpected", data)
    ]
