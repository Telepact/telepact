from typing import List, Dict, Any, Optional, TYPE_CHECKING
from uapi.internal.types.UStruct import _STRUCT_NAME

if TYPE_CHECKING:
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure


def validate_struct(value: Any, select: Optional[Dict[str, Any]], fn: str,
                    type_parameters: List['UTypeDeclaration'], generics: List['UTypeDeclaration'],
                    name: str, fields: Dict[str, 'UFieldDeclaration']) -> List['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from uapi.internal.validation.ValidateStructFields import validate_struct_fields

    if isinstance(value, dict):
        selected_fields = select.get(name) if select else None
        return validate_struct_fields(fields, selected_fields, value, select, fn, type_parameters)
    else:
        return get_type_unexpected_validation_failure([], value, _STRUCT_NAME)
