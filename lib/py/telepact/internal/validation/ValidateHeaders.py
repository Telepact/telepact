from typing import TYPE_CHECKING
from ...internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from ..types.VFieldDeclaration import VFieldDeclaration
    from ..types.VFn import VFn


def validate_headers(headers: dict[str, object], parsed_request_headers: dict[str, 'VFieldDeclaration'], function_type: 'VFn') -> list['ValidationFailure']:
    from ...internal.validation.ValidateContext import ValidateContext

    validation_failures = []

    for header, header_value in headers.items():
        field = parsed_request_headers.get(header)
        if field:
            this_validation_failures = field.type_declaration.validate(
                header_value, ValidateContext(None, function_type.name))
            this_validation_failures_path = [
                ValidationFailure([header] + e.path, e.reason, e.data)
                for e in this_validation_failures
            ]
            validation_failures.extend(this_validation_failures_path)

    return validation_failures
