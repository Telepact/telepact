from typing import List, Dict, Any
from uapi.internal.types import UStruct
from uapi.internal.validation import GetTypeUnexpectedValidationFailure


def validate_select_struct(struct_reference: UStruct, base_path: List[Any], selected_fields: Any) -> List[ValidationFailure]:
    validation_failures = []

    if not isinstance(selected_fields, list):
        return GetTypeUnexpectedValidationFailure(base_path, selected_fields, "Array")

    fields = selected_fields

    for i, field in enumerate(fields):
        if not isinstance(field, str):
            this_path = base_path + [i]
            validation_failures.extend(
                GetTypeUnexpectedValidationFailure(this_path, field, "String"))
            continue

        string_field = field

        if string_field not in struct_reference.fields:
            this_path = base_path + [i]
            validation_failures.append(ValidationFailure(
                this_path, "ObjectKeyDisallowed", {}))

    return validation_failures
