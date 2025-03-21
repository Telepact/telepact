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

class MockStub:
    def __init__(self, when_function: str, when_argument: dict[str, object],
                 then_result: dict[str, object], allow_argument_partial_match: bool, count: int) -> None:
        self.when_function = when_function
        self.when_argument = when_argument
        self.then_result = then_result
        self.allow_argument_partial_match = allow_argument_partial_match
        self.count = count
