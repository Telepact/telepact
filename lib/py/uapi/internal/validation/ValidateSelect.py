from typing import TYPE_CHECKING, cast
from uapi.internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.types.UType import UType


def validate_select(given_obj: object, select: dict[str, object] | None, fn: str | None,
                    type_parameters: list['UTypeDeclaration'],
                    types: dict[str, 'UType']) -> list['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from uapi.internal.validation.ValidateSelectStruct import validate_select_struct
    from uapi.internal.types.UUnion import UUnion
    from uapi.internal.types.UFn import UFn
    from uapi.internal.types.UStruct import UStruct

    if not isinstance(given_obj, dict):
        return get_type_unexpected_validation_failure([], given_obj, "Object")

    select_struct_fields_header = given_obj

    validation_failures = []
    function_type = cast(UFn, types[cast(str, fn)])

    for entry in select_struct_fields_header.items():
        type_name, select_value = entry

        type_reference: 'UType'
        if type_name == "->":
            type_reference = function_type.result
        else:
            possible_type_reference = types.get(type_name)
            if possible_type_reference is None:
                validation_failures.append(ValidationFailure(
                    [type_name], "ObjectKeyDisallowed", {}))
                continue

            type_reference = possible_type_reference

        if isinstance(type_reference, UUnion):
            u = type_reference
            if not isinstance(select_value, dict):
                validation_failures.extend(
                    get_type_unexpected_validation_failure([type_name], select_value, "Object"))
                continue

            union_cases = select_value

            for union_case_entry in union_cases.items():
                union_case, selected_case_struct_fields = union_case_entry
                struct_ref = u.cases.get(union_case)

                loop_path = [type_name, union_case]

                if struct_ref is None:
                    validation_failures.append(ValidationFailure(
                        loop_path, "ObjectKeyDisallowed", {}))
                    continue

                nested_validation_failures = validate_select_struct(
                    struct_ref, loop_path, selected_case_struct_fields)

                validation_failures.extend(nested_validation_failures)
        elif isinstance(type_reference, UFn):
            f = type_reference
            fn_call = f.call
            fn_call_cases = fn_call.cases
            fn_name = f.name
            arg_struct = fn_call_cases[fn_name]
            nested_validation_failures = validate_select_struct(
                arg_struct, [type_name], select_value)

            validation_failures.extend(nested_validation_failures)
        elif isinstance(type_reference, UStruct):
            struct_ref = type_reference
            nested_validation_failures = validate_select_struct(
                struct_ref, [type_name], select_value)

            validation_failures.extend(nested_validation_failures)
        else:
            validation_failures.append(ValidationFailure(
                [type_name], "ObjectKeyDisallowed", {}))

    return validation_failures
