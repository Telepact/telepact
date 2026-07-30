#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import NamedTuple

class Response(NamedTuple):
    bytes: bytes
    headers: dict[str, object]

