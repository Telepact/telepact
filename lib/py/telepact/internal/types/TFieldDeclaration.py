#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
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
