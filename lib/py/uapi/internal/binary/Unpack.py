def unpack(value: object) -> object:
    from ...internal.binary.UnpackList import unpack_list

    if isinstance(value, list):
        return unpack_list(value)
    elif isinstance(value, dict):
        new_dict = {}
        for key, val in value.items():
            new_dict[key] = unpack(val)
        return new_dict
    else:
        return value
