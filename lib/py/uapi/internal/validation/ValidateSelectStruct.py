from typing import TYPE_CHECKING
from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
from uapi.internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from uapi.internal.types.UStruct import UStruct


def validate_select_struct(struct_reference: 'UStruct', base_path: list[object], selected_fields: object) -> list['ValidationFailure']:
    validation_failures = []

    if not isinstance(selected_fields, list):
        return get_type_unexpected_validation_failure(base_path, selected_fields, "Array")

    fields = selected_fields

    for i, field in enumerate(fields):
        if not isinstance(field, str):
            this_path = base_path + [i]
            validation_failures.extend(
                get_type_unexpected_validation_failure(this_path, field, "String"))
            continue

        string_field = field

        if string_field not in struct_reference.fields:
            this_path = base_path + [i]
            validation_failures.append(ValidationFailure(
                this_path, "ObjectKeyDisallowed", {}))

    return validation_failures
