#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

class ValidateContext:
    path: list[str]
    select: dict[str, object] | None
    fn: str | None
    coerce_base64: bool
    base64_coercions: dict[str, object]
    bytes_coercions: dict[str, object]

    def __init__(self, 
                 select: dict[str, object] | None = None, 
                 fn: str | None = None, 
                 coerce_base64: bool = False):
        self.path = []
        self.select = select
        self.fn = fn
        self.coerce_base64 = coerce_base64
        self.base64_coercions = {}
        self.bytes_coercions = {}
        
