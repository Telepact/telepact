#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING
from ...internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from ..types.TFieldDeclaration import TFieldDeclaration


def validate_headers(headers: dict[str, object], parsed_request_headers: dict[str, 'TFieldDeclaration'], function_name: str) -> list['ValidationFailure']:
    from ...internal.validation.ValidateContext import ValidateContext

    validation_failures = []

    for header, header_value in headers.items():
        if not header.startswith("@"):
            validation_failures.append(ValidationFailure([header], "RequiredObjectKeyPrefixMissing", {"prefix": "@"}))

        field = parsed_request_headers.get(header)
        if field:
            this_validation_failures = field.type_declaration.validate(
                header_value, ValidateContext(None, function_name))
            this_validation_failures_path = [
                ValidationFailure([header] + e.path, e.reason, e.data)
                for e in this_validation_failures
            ]
            validation_failures.extend(this_validation_failures_path)

    return validation_failures
