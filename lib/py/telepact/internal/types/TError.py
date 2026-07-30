#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .TUnion import TUnion


class TError:
    def __init__(self, name: str, errors: 'TUnion'):
        self.name = name
        self.errors = errors
