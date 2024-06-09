from typing import List, Dict, Set, Any
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure


def offset_schema_index(initial_failures: List['SchemaParseFailure'], offset: int, schema_keys_to_index: Dict[str, int], error_indices: Set[int]) -> List['SchemaParseFailure']:
    final_list = []

    index_to_schema_key = {v: k for k, v in schema_keys_to_index.items()}

    for f in initial_failures:
        reason = f.reason
        path = f.path
        data = f.data
        new_path = list(path)

        original_index = new_path[0]
        new_path[0] = original_index - offset

        if reason == "PathCollision":
            other_new_path = list(data["other"])
            other_new_path[0] = other_new_path[0] - offset
            final_data = {"other": other_new_path}
        else:
            final_data = data

        if original_index in error_indices:
            schema_key = "errors"
        else:
            schema_key = index_to_schema_key.get(original_index)

        final_list.append(SchemaParseFailure(
            new_path, reason, final_data, schema_key))

    return final_list
