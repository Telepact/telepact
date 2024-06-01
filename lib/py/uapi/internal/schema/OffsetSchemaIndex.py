from typing import List, Dict, Set, Any


def offset_schema_index(initial_failures: List[Dict[str, Any]], offset: int,
                        schema_keys_to_index: Dict[str, int], error_indices: Set[int]) -> List[Dict[str, Any]]:
    final_list = []

    index_to_schema_key = {v: k for k, v in schema_keys_to_index.items()}

    for f in initial_failures:
        reason = f['reason']
        path = f['path']
        data = f['data']
        new_path = list(path)

        original_index = new_path[0]
        new_path[0] = original_index - offset

        final_data = {}
        if reason == "PathCollision":
            other_new_path = list(data['other'])
            other_new_path[0] = other_new_path[0] - offset
            final_data = {"other": other_new_path}
        else:
            final_data = data

        schema_key = "errors" if original_index in error_indices else index_to_schema_key.get(
            original_index)

        final_list.append({"path": new_path, "reason": reason,
                          "data": final_data, "schema_key": schema_key})

    return final_list
