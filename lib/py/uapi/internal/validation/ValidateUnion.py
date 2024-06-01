from typing import Any, Dict, List, Optional

from uapi.internal.types.UStruct import UStruct
from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
from uapi.internal.types.UUnion import _UNION_NAME
from uapi.internal.validation.ValidateUnionCases import validate_union_cases
from uapi.internal.validation.ValidationFailure import ValidationFailure
from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure


def validate_union(value: Any, select: Optional[Dict[str, Any]], fn: str,
                   type_parameters: List['UTypeDeclaration'], generics: List['UTypeDeclaration'],
                   name: str, cases: Dict[str, 'UStruct']) -> List['ValidationFailure']:
    if isinstance(value, dict):
        selected_cases: Dict[str, Any]
        if name.startswith("fn."):
            selected_cases = {name: select.get(name) if select else None}
        else:
            selected_cases = select.get(name) if select else None
        return validate_union_cases(cases, selected_cases, value, select, fn, type_parameters)
    else:
        return get_type_unexpected_validation_failure([], value, _UNION_NAME)
