from typing import TYPE_CHECKING, cast
from uapi.internal.types.UUnion import _UNION_NAME
from uapi.internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def validate_union(value: object, select: dict[str, object] | None, fn: str | None,
                   name: str, cases: dict[str, 'UStruct']) -> list['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from uapi.internal.validation.ValidateUnionCases import validate_union_cases

    if isinstance(value, dict):
        selected_cases: dict[str, object]
        if name.startswith("fn."):
            selected_cases = {name: select.get(name) if select else None}
        else:
            selected_cases = cast(
                dict[str, object], select.get(name) if select else None)
        return validate_union_cases(cases, selected_cases, value, select, fn)
    else:
        return get_type_unexpected_validation_failure([], value, _UNION_NAME)
