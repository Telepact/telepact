#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

def unpack_body(body: dict[object, object]) -> dict[object, object]:
    from ...internal.binary.Unpack import unpack

    result = {}

    for key, value in body.items():
        unpacked_value = unpack(value)
        result[key] = unpacked_value

    return result
