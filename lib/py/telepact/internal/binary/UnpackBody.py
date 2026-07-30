#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from .Unpack import unpack


def unpack_body(body: dict[object, object]) -> dict[object, object]:
    return {key: unpack(value) for key, value in body.items()}
