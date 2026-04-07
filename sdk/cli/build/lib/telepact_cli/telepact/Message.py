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

from typing import cast, NamedTuple


class Message(NamedTuple):
    headers: dict[str, object]
    body: dict[str, object]

    def get_body_target(self) -> str:
        entry = next(iter(self.body.items()))
        return entry[0]

    def get_body_payload(self) -> dict[str, object]:
        entry = next(iter(self.body.items()))
        return cast(dict[str, object], entry[1])
