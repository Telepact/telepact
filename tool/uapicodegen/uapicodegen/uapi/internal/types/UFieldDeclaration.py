from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...internal.types.UTypeDeclaration import UTypeDeclaration


class UFieldDeclaration:
    def __init__(
            self,
            field_name: str,
            type_declaration: 'UTypeDeclaration',
            optional: bool
    ) -> None:
        self.field_name = field_name
        self.type_declaration = type_declaration
        self.optional = optional
