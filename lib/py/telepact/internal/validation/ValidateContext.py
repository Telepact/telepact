#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
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
        
