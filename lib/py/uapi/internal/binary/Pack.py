from typing import list, dict, object


def pack(value: object) -> object:
    from uapi.internal.binary.Packlist import pack_list

    if isinstance(value, list):
        return pack_list(value)
    elif isinstance(value, dict):
        new_map = {}

        for key, val in value.items():
            new_map[key] = pack(val)

        return new_map
    else:
        return value
