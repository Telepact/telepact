#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from typing import TYPE_CHECKING

from ...internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ..types.TFieldDeclaration import TFieldDeclaration
    from ..types.TTypeDeclaration import TTypeDeclaration


def validate_struct_fields(fields: dict[str, 'TFieldDeclaration'],
                           selected_fields: list[str] | None,
                           actual_struct: dict[str, object],
                           ctx: 'ValidateContext') -> list['ValidationFailure']:
    validation_failures = []
    optional_wire_key_hints = _get_optional_wire_key_hints(fields)

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
            optional_wire_key_hint = optional_wire_key_hints.get(field_name)
            if optional_wire_key_hint is not None:
                validation_failures.append(ValidationFailure(
                    [field_name],
                    "ExtensionValidationFailed",
                    {
                        "reason": "Optional struct fields keep the ! suffix on the wire; prefer generated helpers to set them.",
                        "data": {
                            "receivedKey": field_name,
                            "expectedWireKey": optional_wire_key_hint,
                        },
                    },
                ))
            continue

        ref_field_type_declaration = reference_field.type_declaration

        ctx.path.append(field_name)

        nested_validation_failures = ref_field_type_declaration.validate(
            field_value, ctx)
        
        ctx.path.pop()
        
        nested_validation_failures_with_path = []
        for failure in nested_validation_failures:
            this_path = [field_name] + failure.path

            nested_validation_failures_with_path.append(
                ValidationFailure(this_path, failure.reason, failure.data))

        validation_failures.extend(nested_validation_failures_with_path)

    return validation_failures


def _get_optional_wire_key_hints(fields: dict[str, 'TFieldDeclaration']) -> dict[str, str]:
    optional_wire_key_hints: dict[str, str] = {}
    for field_name in fields:
        if not field_name.endswith('!'):
            continue
        optional_wire_key_hints[field_name[:-1]] = field_name
    return optional_wire_key_hints
