from typing import Any, Dict, List, Union
from uapi.internal.types import UFn, UStruct, UType, UTypeDeclaration, UUnion
from uapi.internal.validation.GetTypeUnexpectedValidationFailure import getTypeUnexpectedValidationFailure
from uapi.internal.validation.ValidateSelectStruct import validateSelectStruct


def validate_select(given_obj: Any, select: Dict[str, Any], fn: str,
                    type_parameters: List[UTypeDeclaration], generics: List[UTypeDeclaration],
                    types: Dict[str, UType]) -> List[ValidationFailure]:

    if not isinstance(given_obj, dict):
        return getTypeUnexpectedValidationFailure([], given_obj, "Object")

    select_struct_fields_header = given_obj

    validation_failures = []
    function_type = types[fn]

    for entry in select_struct_fields_header.items():
        type_name, select_value = entry

        if type_name == "->":
            type_reference = function_type.result
        else:
            type_reference = types.get(type_name)

        if type_reference is None:
            validation_failures.append(ValidationFailure(
                [type_name], "ObjectKeyDisallowed", {}))
            continue

        if isinstance(type_reference, UUnion):
            if not isinstance(select_value, dict):
                validation_failures.extend(
                    getTypeUnexpectedValidationFailure([type_name], select_value, "Object"))
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

                nested_validation_failures = validateSelectStruct(
                    struct_ref, loop_path, selected_case_struct_fields)

                validation_failures.extend(nested_validation_failures)
        elif isinstance(type_reference, UFn):
            fn_call = f.call
            fn_call_cases = fn_call.cases
            fn_name = f.name
            arg_struct = fn_call_cases.get(fn_name)
            nested_validation_failures = validateSelectStruct(
                arg_struct, [type_name], select_value)

            validation_failures.extend(nested_validation_failures)
        else:
            struct_ref = type_reference
            nested_validation_failures = validateSelectStruct(
                struct_ref, [type_name], select_value)

            validation_failures.extend(nested_validation_failures)

    return validation_failures
