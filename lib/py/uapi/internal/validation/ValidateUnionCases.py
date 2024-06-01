from typing import List, Dict, Any, Union
from uapi.internal.types import UStruct, UTypeDeclaration
from uapi.internal.validation.GetTypeUnexpectedValidationFailure import getTypeUnexpectedValidationFailure
from uapi.internal.validation.ValidateUnionStruct import validate_union_struct


def validate_union_cases(reference_cases: Dict[str, UStruct], selected_cases: Dict[str, Any],
                         actual: Dict[Any, Any], select: Dict[str, Any], fn: str,
                         type_parameters: List[UTypeDeclaration]) -> List[ValidationFailure]:
    if len(actual) != 1:
        return [
            ValidationFailure([], "ObjectSizeUnexpected", {
                              "actual": len(actual), "expected": 1})
        ]

    union_target, union_payload = next(iter(actual.items()))

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
        return getTypeUnexpectedValidationFailure([union_target], union_payload, "Object")
