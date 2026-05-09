#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

class BinaryPackNode:
    def __init__(self, value: int, nested: dict[int, 'BinaryPackNode']):
        self.value = value
        self.nested = nested
