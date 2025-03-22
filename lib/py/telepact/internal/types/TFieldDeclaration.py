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

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .TTypeDeclaration import TTypeDeclaration


class TFieldDeclaration:
    def __init__(
            self,
            field_name: str,
            type_declaration: 'TTypeDeclaration',
            optional: bool
    ) -> None:
        self.field_name = field_name
        self.type_declaration = type_declaration
        self.optional = optional
