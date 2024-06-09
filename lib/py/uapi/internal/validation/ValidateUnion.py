from typing import Any, Dict, List, Optional, TYPE_CHECKING
from uapi.internal.types.UUnion import _UNION_NAME
from uapi.internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def validate_union(value: Any, select: Optional[Dict[str, Any]], fn: str,
                   type_parameters: List['UTypeDeclaration'], generics: List['UTypeDeclaration'],
                   name: str, cases: Dict[str, 'UStruct']) -> List['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from uapi.internal.validation.ValidateUnionCases import validate_union_cases

    if isinstance(value, dict):
        selected_cases: Dict[str, Any]
        if name.startswith("fn."):
            selected_cases = {name: select.get(name) if select else None}
        else:
            selected_cases = select.get(name) if select else None
        return validate_union_cases(cases, selected_cases, value, select, fn, type_parameters)
    else:
        return get_type_unexpected_validation_failure([], value, _UNION_NAME)
