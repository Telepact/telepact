#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from .Pack import pack


def pack_body(body: dict[object, object]) -> dict[object, object]:
    return {key: pack(value) for key, value in body.items()}
