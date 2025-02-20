from typing import TYPE_CHECKING, cast

from ..internal.types.UArray import UArray
from ..internal.types.UFn import UFn
from ..internal.types.UObject import UObject
from ..internal.types.UStruct import UStruct
from ..internal.types.UUnion import UUnion

if TYPE_CHECKING:
    from ..internal.types.UTypeDeclaration import UTypeDeclaration


def select_struct_fields(type_declaration: 'UTypeDeclaration', value: object,
                         selected_struct_fields: dict[str, object]) -> object:
    type_declaration_type = type_declaration.type
    type_declaration_type_params = type_declaration.type_parameters

    if isinstance(type_declaration_type, UStruct):
        fields = type_declaration_type.fields
        struct_name = type_declaration_type.name
        selected_fields = cast(
            list[str] | None, selected_struct_fields.get(struct_name))
        value_as_map = cast(dict[str, object], value)
        final_map = {}

        for field_name, field_value in value_as_map.items():
            if selected_fields is None or field_name in selected_fields:
                field = fields[field_name]
                field_type_declaration = field.type_declaration
                value_with_selected_fields = select_struct_fields(field_type_declaration, field_value,
                                                                  selected_struct_fields)

                final_map[field_name] = value_with_selected_fields

        return final_map
    elif isinstance(type_declaration_type, UFn):
        value_as_map = cast(dict[str, object], value)
        union_tag, union_data = cast(
            tuple[str, dict[str, object]], next(iter(value_as_map.items())))

        fn_name = type_declaration_type.name
        fn_call = type_declaration_type.call
        fn_call_tags = fn_call.tags

        arg_struct_reference = fn_call_tags[union_tag]
        selected_fields = cast(
            list[str] | None, selected_struct_fields.get(fn_name))
        final_map = {}

        for field_name, field_value in union_data.items():
            if selected_fields is None or field_name in selected_fields:
                field = arg_struct_reference.fields[field_name]
                value_with_selected_fields = select_struct_fields(field.type_declaration, field_value,
                                                                  selected_struct_fields)

                final_map[field_name] = value_with_selected_fields

        return {union_tag: final_map}
    elif isinstance(type_declaration_type, UUnion):
        value_as_map = cast(dict[str, object], value)
        union_tag, union_data = cast(
            tuple[str, dict[str, object]], next(iter(value_as_map.items())))

        union_tags = type_declaration_type.tags
        union_struct_reference = union_tags[union_tag]
        union_struct_ref_fields = union_struct_reference.fields
        default_tags_to_fields = {}

        for tag, union_struct in union_tags.items():
            field_names = list(union_struct.fields.keys())
            default_tags_to_fields[tag] = field_names

        union_selected_fields = cast(dict[str, object], selected_struct_fields.get(
            type_declaration_type.name, default_tags_to_fields))
        this_union_tag_selected_fields_default = default_tags_to_fields.get(
            union_tag)
        selected_fields = cast(list[str] | None, union_selected_fields.get(
            union_tag, this_union_tag_selected_fields_default))

        final_map = {}
        for field_name, field_value in union_data.items():
            if selected_fields is None or field_name in selected_fields:
                field = union_struct_ref_fields[field_name]
                value_with_selected_fields = select_struct_fields(field.type_declaration, field_value,
                                                                  selected_struct_fields)

                final_map[field_name] = value_with_selected_fields

        return {union_tag: final_map}
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
