#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from .UnpackList import unpack_list


def unpack(value: object) -> object:
    value_type = type(value)
    if value_type is list:
        return unpack_list(value)
    if value_type is dict:
        new_dict = {}
        for key, val in value.items():
            new_dict[key] = unpack(val)
        return new_dict
    return value
