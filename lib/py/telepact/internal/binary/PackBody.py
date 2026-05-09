#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

def pack_body(body: dict[object, object]) -> dict[object, object]:
    from ...internal.binary.Pack import pack

    result = {}

    for key, value in body.items():
        packed_value = pack(value)
        result[key] = packed_value

    return result
