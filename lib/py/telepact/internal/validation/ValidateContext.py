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
    use_bytes: bool
    expect_bytes: bool | None
    new_value: object | None
    coercions: dict[str, object]

    def __init__(self, select: dict[str, object] | None = None, fn: str | None = None, expect_bytes: bool = False, use_bytes: bool = False):
        self.path = []
        self.select = select
        self.fn = fn
        self.expect_bytes = expect_bytes
        self.use_bytes = use_bytes
        self.new_value = None
        self.coercions = {}
