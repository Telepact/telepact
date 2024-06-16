from typing import TYPE_CHECKING
from uapi.internal.types.UArray import _ARRAY_NAME
from uapi.internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def validate_array(value: object, select: dict[str, object] | None, fn: str | None,
                   type_parameters: list['UTypeDeclaration'],
                   generics: list['UTypeDeclaration']) -> list['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if isinstance(value, list):
        nested_type_declaration = type_parameters[0]

        validation_failures = []
        for i, element in enumerate(value):
            nested_validation_failures = nested_type_declaration.validate(
                element, select, fn, generics)
            index = i

            nested_validation_failures_with_path = []
            for f in nested_validation_failures:
                final_path = [index] + f.path

                nested_validation_failures_with_path.append(
                    ValidationFailure(final_path, f.reason, f.data))

            validation_failures.extend(nested_validation_failures_with_path)

        return validation_failures
    else:
        return get_type_unexpected_validation_failure([], value, _ARRAY_NAME)
