from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .VTypeDeclaration import VTypeDeclaration


class VFieldDeclaration:
    def __init__(
            self,
            field_name: str,
            type_declaration: 'VTypeDeclaration',
            optional: bool
    ) -> None:
        self.field_name = field_name
        self.type_declaration = type_declaration
        self.optional = optional
