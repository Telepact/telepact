#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

class BinaryEncodingMissing(Exception):
    def __init__(self, key: object) -> None:
        super().__init__(f"Missing binary encoding for {str(key)}")
