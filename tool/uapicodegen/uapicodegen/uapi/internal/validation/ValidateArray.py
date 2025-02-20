from typing import TYPE_CHECKING
from ...internal.types.UArray import _ARRAY_NAME
from ...internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ...internal.types.UTypeDeclaration import UTypeDeclaration


def validate_array(value: object,
                   type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if isinstance(value, list):
        nested_type_declaration = type_parameters[0]

        validation_failures = []
        for i, element in enumerate(value):
            nested_validation_failures = nested_type_declaration.validate(
                element, ctx)
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
