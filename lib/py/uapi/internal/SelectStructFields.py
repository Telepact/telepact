from typing import TYPE_CHECKING, cast

from uapi.internal.types.UArray import UArray
from uapi.internal.types.UFn import UFn
from uapi.internal.types.UObject import UObject
from uapi.internal.types.UStruct import UStruct
from uapi.internal.types.UUnion import UUnion

if TYPE_CHECKING:
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def select_struct_fields(type_declaration: 'UTypeDeclaration', value: object,
                         selected_struct_fields: dict[str, object]) -> object:
    type_declaration_type = type_declaration.type
    type_declaration_type_params = type_declaration.type_parameters

    if isinstance(type_declaration_type, UStruct):
        fields = type_declaration_type.fields
        struct_name = type_declaration_type.name
        selected_fields = cast(
            list[str], selected_struct_fields.get(struct_name, []))
        value_as_map = cast(dict[str, object], value)
        final_map = {}

        for field_name, field_value in value_as_map.items():
            if not selected_fields or field_name in selected_fields:
                field = fields[field_name]
                field_type_declaration = field.type_declaration
                value_with_selected_fields = select_struct_fields(field_type_declaration, field_value,
                                                                  selected_struct_fields)

                final_map[field_name] = value_with_selected_fields

        return final_map
    elif isinstance(type_declaration_type, UFn):
        value_as_map = cast(dict[str, object], value)
        union_case, union_data = cast(
            tuple[str, dict[str, object]], next(iter(value_as_map.items())))

        fn_name = type_declaration_type.name
        fn_call = type_declaration_type.call
        fn_call_cases = fn_call.cases

        arg_struct_reference = fn_call_cases[union_case]
        selected_fields = cast(
            list[str], selected_struct_fields.get(fn_name, []))
        final_map = {}

        for field_name, field_value in union_data.items():
            if not selected_fields or field_name in selected_fields:
                field = arg_struct_reference.fields[field_name]
                value_with_selected_fields = select_struct_fields(field.type_declaration, field_value,
                                                                  selected_struct_fields)

                final_map[field_name] = value_with_selected_fields

        return {union_case: final_map}
    elif isinstance(type_declaration_type, UUnion):
        value_as_map = cast(dict[str, object], value)
        union_case, union_data = cast(
            tuple[str, dict[str, object]], next(iter(value_as_map.items())))

        union_cases = type_declaration_type.cases
        union_struct_reference = union_cases[union_case]
        union_struct_ref_fields = union_struct_reference.fields
        default_cases_to_fields = {}

        for case, union_struct in union_cases.items():
            field_names = list(union_struct.fields.keys())
            default_cases_to_fields[case] = field_names

        union_selected_fields = cast(dict[str, object], selected_struct_fields.get(
            type_declaration_type.name, default_cases_to_fields))
        this_union_case_selected_fields_default = default_cases_to_fields.get(
            union_case)
        selected_fields = cast(list[str], union_selected_fields.get(
            union_case, this_union_case_selected_fields_default))

        final_map = {}
        for field_name, field_value in union_data.items():
            if not selected_fields or field_name in selected_fields:
                field = union_struct_ref_fields[field_name]
                value_with_selected_fields = select_struct_fields(field.type_declaration, field_value,
                                                                  selected_struct_fields)

                final_map[field_name] = value_with_selected_fields

        return {union_case: final_map}
    elif isinstance(type_declaration_type, UObject):
        nested_type_declaration = type_declaration_type_params[0]
        value_as_map = cast(dict[str, object], value)

        final_map = {}
        for key, value in value_as_map.items():
            value_with_selected_fields = select_struct_fields(nested_type_declaration, value,
                                                              selected_struct_fields)

            final_map[key] = value_with_selected_fields

        return final_map
    elif isinstance(type_declaration_type, UArray):
        nested_type = type_declaration_type_params[0]
        value_as_list = cast(list[str], value)

        final_list = []
        for entry in value_as_list:
            value_with_selected_fields = select_struct_fields(
                nested_type, entry, selected_struct_fields)
            final_list.append(value_with_selected_fields)

        return final_list
    else:
        return value
