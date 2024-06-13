from typing import TYPE_CHECKING, cast
from uapi.internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def validate_union_cases(reference_cases: dict[str, 'UStruct'], selected_cases: dict[str, object],
                         actual: dict[object, object], select: dict[str, object] | None, fn: str | None,
                         type_parameters: list['UTypeDeclaration']) -> list['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from uapi.internal.validation.ValidateUnionStruct import validate_union_struct

    if len(actual) != 1:
        return [
            ValidationFailure([], "ObjectSizeUnexpected", {
                              "actual": len(actual), "expected": 1})
        ]

    union_target, union_payload = cast(
        tuple[str, object], next(iter(actual.items())))

    reference_struct = reference_cases.get(union_target)
    if reference_struct is None:
        return [
            ValidationFailure([union_target], "ObjectKeyDisallowed", {})
        ]

    if isinstance(union_payload, dict):
        nested_validation_failures = validate_union_struct(reference_struct, union_target,
                                                           union_payload, selected_cases, select, fn, type_parameters)

        nested_validation_failures_with_path = []
        for failure in nested_validation_failures:
            this_path = [union_target] + failure.path
            nested_validation_failures_with_path.append(
                ValidationFailure(this_path, failure.reason, failure.data)
            )

        return nested_validation_failures_with_path
    else:
        return get_type_unexpected_validation_failure([union_target], union_payload, "Object")
