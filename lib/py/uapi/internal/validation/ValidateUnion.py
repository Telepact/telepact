from typing import Any, Dict, List, Optional
from uapi.internal.types import UStruct, UTypeDeclaration
from uapi.internal.validation import GetTypeUnexpectedValidationFailure, validateUnionCases


def validate_union(value: Any, select: Optional[Dict[str, Any]], fn: str,
                   type_parameters: List[UTypeDeclaration], generics: List[UTypeDeclaration],
                   name: str, cases: Dict[str, UStruct]) -> List[ValidationFailure]:
    if isinstance(value, dict):
        selected_cases: Dict[str, Any]
        if name.startswith("fn."):
            selected_cases = {name: select.get(name) if select else None}
        else:
            selected_cases = select.get(name) if select else None
        return validateUnionCases(cases, selected_cases, value, select, fn, type_parameters)
    else:
        return GetTypeUnexpectedValidationFailure([], value, _UNION_NAME)
