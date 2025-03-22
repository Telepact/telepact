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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .TFieldDeclaration import TFieldDeclaration


class THeaders:
    def __init__(
            self,
            name: str,
            request_headers: dict[str, 'TFieldDeclaration'],
            response_headers: dict[str, 'TFieldDeclaration']
    ) -> None:
        self.name = name
        self.request_headers = request_headers
        self.response_headers = response_headers
