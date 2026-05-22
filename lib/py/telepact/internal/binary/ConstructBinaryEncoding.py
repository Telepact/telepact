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

from ...internal.binary.BinaryEncoding import BinaryEncoding
from ...internal.binary.CreateChecksum import create_checksum

if TYPE_CHECKING:
    from ...TelepactSchema import TelepactSchema
    from ..types.TTypeDeclaration import TTypeDeclaration


def trace_type(type_declaration: 'TTypeDeclaration', visited_type_names: set[str] | None = None) -> list[str]:
    from ..types.TArray import TArray
    from ..types.TObject import TObject
    from ..types.TStruct import TStruct
    from ..types.TUnion import TUnion

    if visited_type_names is None:
        visited_type_names = set()

    this_all_keys: list[str] = []

    if isinstance(type_declaration.type, TArray):
        these_keys2 = trace_type(type_declaration.type_parameters[0], visited_type_names)
        this_all_keys.extend(these_keys2)
    elif isinstance(type_declaration.type, TObject):
        these_keys2 = trace_type(type_declaration.type_parameters[0], visited_type_names)
        this_all_keys.extend(these_keys2)
    elif isinstance(type_declaration.type, TStruct):
        if type_declaration.type.name in visited_type_names:
            return this_all_keys
        visited_type_names.add(type_declaration.type.name)
        struct_fields = type_declaration.type.fields
        for struct_field_key, struct_field in struct_fields.items():
            this_all_keys.append(struct_field_key)
            more_keys = trace_type(struct_field.type_declaration, visited_type_names)
            this_all_keys.extend(more_keys)
    elif isinstance(type_declaration.type, TUnion):
        if type_declaration.type.name in visited_type_names:
            return this_all_keys
        visited_type_names.add(type_declaration.type.name)
        union_tags = type_declaration.type.tags
        for tag_key, tag_value in union_tags.items():
            this_all_keys.append(tag_key)
            struct_fields = tag_value.fields
            for struct_field_key, struct_field in struct_fields.items():
                this_all_keys.append(struct_field_key)
                more_keys = trace_type(struct_field.type_declaration, visited_type_names)
                this_all_keys.extend(more_keys)

    return this_all_keys


def build_pack_header(field_key: str | None, type_declaration: 'TTypeDeclaration') -> list[object]:
    from ..types.TStruct import TStruct

    if not isinstance(type_declaration.type, TStruct):
        raise ValueError("pack headers can only be built from struct types")

    header: list[object] = [field_key]
    for nested_field_key, nested_field in type_declaration.type.fields.items():
        if nested_field.type_declaration.nullable:
            header.append(nested_field_key)
            continue

        if isinstance(nested_field.type_declaration.type, TStruct):
            header.append(build_pack_header(nested_field_key, nested_field.type_declaration))
        else:
            header.append(nested_field_key)

    return header


def insert_pack_site(pack_site_tree: dict[str, object], path: list[str], header: list[object]) -> None:
    cursor = pack_site_tree

    for part in path[:-1]:
        existing = cursor.get(part)
        if existing is None:
            child: dict[str, object] = {}
            cursor[part] = child
            cursor = child
            continue

        if type(existing) is not dict:
            raise ValueError("pack site tree cannot branch beneath a pack header leaf")

        cursor = cast(dict[str, object], existing)

    leaf_key = path[-1]
    existing_leaf = cursor.get(leaf_key)
    if existing_leaf is not None:
        raise ValueError(f"duplicate pack site path: {'/'.join(path)}")

    cursor[leaf_key] = header


def collect_pack_sites(type_declaration: 'TTypeDeclaration', path: list[str],
                       under_generic_list: bool = False,
                       under_object_map: bool = False) -> list[list[object]]:
    from ..types.TArray import TArray
    from ..types.TObject import TObject
    from ..types.TStruct import TStruct
    from ..types.TUnion import TUnion

    type_ = type_declaration.type

    if isinstance(type_, TObject):
        return collect_pack_sites(type_declaration.type_parameters[0], path,
                                  under_generic_list=under_generic_list,
                                  under_object_map=True)

    if isinstance(type_, TArray):
        item_type = type_declaration.type_parameters[0]
        if not under_generic_list and not under_object_map and isinstance(item_type.type, TStruct):
            return [[list(path), build_pack_header(None, item_type)]]

        return collect_pack_sites(item_type, path, under_generic_list=True,
                                  under_object_map=under_object_map)

    if isinstance(type_, TStruct):
        pack_sites: list[list[object]] = []
        for field_key, field in type_.fields.items():
            pack_sites.extend(collect_pack_sites(field.type_declaration, path + [field_key],
                                                 under_generic_list=under_generic_list,
                                                 under_object_map=under_object_map))
        return pack_sites

    if isinstance(type_, TUnion):
        union_pack_sites: list[list[object]] = []
        for tag_key, tag_value in type_.tags.items():
            for field_key, field in tag_value.fields.items():
                union_pack_sites.extend(collect_pack_sites(
                    field.type_declaration,
                    path + [tag_key, field_key],
                    under_generic_list=under_generic_list,
                    under_object_map=under_object_map,
                ))
        return union_pack_sites

    return []


def construct_binary_encoding(telepact_schema: 'TelepactSchema') -> 'BinaryEncoding':
    from ..types.TUnion import TUnion

    all_keys: set[str] = set()
    pack_site_tree: dict[str, object] = {}

    for key, value in telepact_schema.parsed.items():

        if key.endswith('.->') and isinstance(value, TUnion):
            function_name = key[:-3]
            result = value.tags['Ok_']
            all_keys.add(function_name)
            all_keys.add('Ok_')
            for field_key, field in result.fields.items():
                all_keys.add(field_key)
                keys = trace_type(field.type_declaration)
                for nested_key in keys:
                    all_keys.add(nested_key)
                for pack_site in collect_pack_sites(field.type_declaration, [function_name, '->', 'Ok_', field_key]):
                    insert_pack_site(pack_site_tree, cast(list[str], pack_site[0]), cast(list[object], pack_site[1]))

        elif key.startswith('fn.') and isinstance(value, TUnion):
            all_keys.add(key)
            args = value.tags[key]
            for field_key, field in args.fields.items():
                all_keys.add(field_key)
                keys = trace_type(field.type_declaration)
                for nested_key in keys:
                    all_keys.add(nested_key)
                for pack_site in collect_pack_sites(field.type_declaration, [key, field_key]):
                    insert_pack_site(pack_site_tree, cast(list[str], pack_site[0]), cast(list[object], pack_site[1]))

    sorted_all_keys = sorted(all_keys)

    binary_encoding = {key: i for i, key in enumerate(sorted_all_keys)}
    final_string = "\n".join(sorted_all_keys)
    checksum = create_checksum(final_string)
    return BinaryEncoding(binary_encoding, checksum, pack_site_tree)
