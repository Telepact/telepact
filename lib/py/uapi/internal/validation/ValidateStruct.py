from typing import List, Dict, Any, Optional
from uapi.internal.types import UFieldDeclaration, UTypeDeclaration
from uapi.internal.validation.GetTypeUnexpectedValidationFailure import getTypeUnexpectedValidationFailure
from uapi.internal.validation.ValidateStructFields import validate_struct_fields


def validate_struct(value: Any, select: Optional[Dict[str, Any]], fn: str,
                    type_parameters: List[UTypeDeclaration], generics: List[UTypeDeclaration],
                    name: str, fields: Dict[str, UFieldDeclaration]) -> List[ValidationFailure]:
    if isinstance(value, dict):
        selected_fields = select.get(name) if select else None
        return validate_struct_fields(fields, selected_fields, value, select, fn, type_parameters)
    else:
        return getTypeUnexpectedValidationFailure([], value, _STRUCT_NAME)
