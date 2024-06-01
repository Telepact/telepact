from typing import List, Dict
from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
from uapi.internal.types.UFn import UFn
from uapi.internal.validation.ValidationFailure import ValidationFailure


def validate_headers(headers: Dict[str, object], parsed_request_headers: Dict[str, 'UFieldDeclaration'], function_type: 'UFn') -> List['ValidationFailure']:
    validation_failures = []

    for header, header_value in headers.items():
        field = parsed_request_headers.get(header)
        if field:
            this_validation_failures = field.type_declaration.validate(
                header_value, None, function_type.name, [])
            this_validation_failures_path = [
                ValidationFailure([header] + e.path, e.reason, e.data)
                for e in this_validation_failures
            ]
            validation_failures.extend(this_validation_failures_path)

    return validation_failures
