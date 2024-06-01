from typing import List, Dict, Any

from uapi.internal.binary.UnpackList import unpack_list


def unpack(value: Any) -> Any:
    if isinstance(value, list):
        return unpack_list(value)
    elif isinstance(value, dict):
        new_dict = {}
        for key, val in value.items():
            new_dict[key] = unpack(val)
        return new_dict
    else:
        return value
