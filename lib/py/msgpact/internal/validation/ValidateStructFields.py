from typing import TYPE_CHECKING

from ...internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ..types.VFieldDeclaration import VFieldDeclaration
    from ..types.VTypeDeclaration import VTypeDeclaration


def validate_struct_fields(fields: dict[str, 'VFieldDeclaration'],
                           selected_fields: list[str] | None,
                           actual_struct: dict[str, object],
                           ctx: 'ValidateContext') -> list['ValidationFailure']:
    validation_failures = []

    missing_fields = []
    for field_name, field_declaration in fields.items():
        is_optional = field_declaration.optional
        is_omitted_by_select = selected_fields is not None and field_name not in selected_fields
        if field_name not in actual_struct and not is_optional and not is_omitted_by_select:
            missing_fields.append(field_name)

    for missing_field in missing_fields:
        validation_failure = ValidationFailure(
            [], "RequiredObjectKeyMissing", {'key': missing_field})

        validation_failures.append(validation_failure)

    for field_name, field_value in actual_struct.items():
        reference_field = fields.get(field_name)
        if reference_field is None:
            validation_failure = ValidationFailure(
                [field_name], "ObjectKeyDisallowed", {})

            validation_failures.append(validation_failure)
            continue

        ref_field_type_declaration = reference_field.type_declaration

        nested_validation_failures = ref_field_type_declaration.validate(
            field_value, ctx)

        nested_validation_failures_with_path = []
        for failure in nested_validation_failures:
            this_path = [field_name] + failure.path

            nested_validation_failures_with_path.append(
                ValidationFailure(this_path, failure.reason, failure.data))

        validation_failures.extend(nested_validation_failures_with_path)

    return validation_failures
