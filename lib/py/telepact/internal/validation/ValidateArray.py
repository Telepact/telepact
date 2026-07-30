#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING
from ..types.TArray import _ARRAY_NAME
from ...internal.validation.ValidationFailure import ValidationFailure
from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ..types.TTypeDeclaration import TTypeDeclaration


def validate_array(value: object,
                   type_parameters: list['TTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
    if type(value) is not list and not isinstance(value, list):
        return get_type_unexpected_validation_failure([], value, _ARRAY_NAME)

    nested_type_declaration = type_parameters[0]

    validation_failures = []
    for i, element in enumerate(value):
        ctx.path.append("*")

        nested_validation_failures = nested_type_declaration.validate(
            element, ctx)
        index = i

        ctx.path.pop()

        if not nested_validation_failures:
            continue

        for f in nested_validation_failures:
            validation_failures.append(
                ValidationFailure([index] + f.path, f.reason, f.data))

    return validation_failures
