from typing import cast
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure


def offset_schema_index(initial_failures: list['SchemaParseFailure'], offset: int, schema_keys_to_index: dict[str, int], error_indices: set[int]) -> list['SchemaParseFailure']:
    final_list = []

    index_to_schema_key = {v: k for k, v in schema_keys_to_index.items()}

    for f in initial_failures:
        reason = f.reason
        path = f.path
        data = cast(dict[str, object], f.data)
        new_path = list(path)

        original_index = cast(int, new_path[0])
        new_path[0] = original_index - offset

        if reason == "PathCollision":
            other_new_path = cast(list[object], data["other"])
            other_new_path[0] = cast(int, other_new_path[0]) - offset
            final_data: dict[str, object] = {"other": other_new_path}
        else:
            final_data = data

        schema_key: str | None
        if original_index in error_indices:
            schema_key = "errors"
        else:
            schema_key = index_to_schema_key.get(original_index, None)

        final_list.append(SchemaParseFailure(
            new_path, reason, final_data, schema_key))

    return final_list
