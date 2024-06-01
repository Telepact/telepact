from typing import Optional


class UFieldDeclaration:
    def __init__(
            self,
            fieldName: str,
            typeDeclaration: 'UTypeDeclaration',
            optional: bool
    ) -> None:
        self.fieldName = fieldName
        self.typeDeclaration = typeDeclaration
        self.optional = optional
