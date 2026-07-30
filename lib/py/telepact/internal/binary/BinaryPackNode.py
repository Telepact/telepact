#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

class BinaryPackNode:
    __slots__ = ("value", "nested")

    def __init__(self, value: int, nested: dict[int, 'BinaryPackNode']):
        self.value = value
        self.nested = nested
