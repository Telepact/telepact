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

from typing import TYPE_CHECKING, cast

from .types.VArray import VArray
from .types.VFn import VFn
from .types.VObject import VObject
from .types.VStruct import VStruct
from .types.VUnion import VUnion

if TYPE_CHECKING:
    from .types.VTypeDeclaration import VTypeDeclaration


def select_struct_fields(type_declaration: 'VTypeDeclaration', value: object,
                         selected_struct_fields: dict[str, object]) -> object:
    type_declaration_type = type_declaration.type
    type_declaration_type_params = type_declaration.type_parameters

    if isinstance(type_declaration_type, VStruct):
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
    elif isinstance(type_declaration_type, VFn):
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
    elif isinstance(type_declaration_type, VUnion):
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
    elif isinstance(type_declaration_type, VObject):
        nested_type_declaration = type_declaration_type_params[0]
        value_as_map = cast(dict[str, object], value)

        final_map = {}
        for key, value in value_as_map.items():
            value_with_selected_fields = select_struct_fields(nested_type_declaration, value,
                                                              selected_struct_fields)

            final_map[key] = value_with_selected_fields

        return final_map
    elif isinstance(type_declaration_type, VArray):
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
