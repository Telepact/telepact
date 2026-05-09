#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ...internal.validation.ValidationFailure import ValidationFailure
    from ..types.TType import TType
    from ..types.TTypeDeclaration import TTypeDeclaration


def validate_value_of_type(value: object,
                           this_type: 'TType',
                           nullable: bool, type_parameters: list['TTypeDeclaration'],
                           ctx: 'ValidateContext') -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if value is None:
        if not nullable:
            return get_type_unexpected_validation_failure([], value, this_type.get_name(ctx))
        else:
            return []

    return this_type.validate(value, type_parameters, ctx)
