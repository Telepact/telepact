from typing import List, Dict, Any


def pack(value: Any) -> Any:
    from uapi.internal.binary.PackList import pack_list

    if isinstance(value, List):
        return pack_list(value)
    elif isinstance(value, Dict):
        new_map = {}

        for key, val in value.items():
            new_map[key] = pack(val)

        return new_map
    else:
        return value
