#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from .PackList import pack_list


def pack(value: object) -> object:
    value_type = type(value)
    if value_type is list:
        return pack_list(value)
    if value_type is dict:
        new_map = {}

        for key, val in value.items():
            new_map[key] = pack(val)

        return new_map
    return value
