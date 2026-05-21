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

from ...internal.binary.BinaryEncoding import BinaryEncoding
from ...internal.binary.CreateChecksum import create_checksum

if TYPE_CHECKING:
    from ...TelepactSchema import TelepactSchema
    from ..types.TTypeDeclaration import TTypeDeclaration


def trace_type(type_declaration: 'TTypeDeclaration', visited_type_names: set[str] | None = None) -> list[str]:
    from ..types.TArray import TArray
    from ..types.TAny import TAny
    from ..types.TObject import TObject
    from ..types.TStruct import TStruct
    from ..types.TUnion import TUnion

    if visited_type_names is None:
        visited_type_names = set()

    this_all_keys: list[str] = []

    if isinstance(type_declaration.type, TArray):
        these_keys2 = trace_type(type_declaration.type_parameters[0], visited_type_names)
        this_all_keys.extend(these_keys2)
    elif isinstance(type_declaration.type, TAny):
        return this_all_keys
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


def _build_pack_header(type_declaration: 'TTypeDeclaration', root_key: str | None = None) -> list[object]:
    from ..types.TStruct import TStruct

    header: list[object] = [root_key]

    if not isinstance(type_declaration.type, TStruct):
        return header

    for field_key, field in type_declaration.type.fields.items():
        if isinstance(field.type_declaration.type, TStruct):
            header.append(_build_pack_header(field.type_declaration, field_key))
        else:
            header.append(field_key)

    return header


def _collect_pack_sites(type_declaration: 'TTypeDeclaration',
                        path: list[str],
                        pack_sites: list[list[object]],
                        active_type_names: set[str] | None = None,
                        under_generic_list: bool = False) -> None:
    from ..types.TArray import TArray
    from ..types.TAny import TAny
    from ..types.TObject import TObject
    from ..types.TStruct import TStruct
    from ..types.TUnion import TUnion

    if active_type_names is None:
        active_type_names = set()

    type_ = type_declaration.type

    if isinstance(type_, TArray):
        item_type = type_declaration.type_parameters[0]
        if not under_generic_list and isinstance(item_type.type, TStruct):
            pack_sites.append([list(path), _build_pack_header(item_type)])
            return
        _collect_pack_sites(item_type, path, pack_sites, active_type_names, True)
        return

    if isinstance(type_, TAny):
        return

    if isinstance(type_, TObject):
        return

    if isinstance(type_, TStruct):
        if type_.name in active_type_names:
            return
        next_active_type_names = set(active_type_names)
        next_active_type_names.add(type_.name)
        for field_key, field in type_.fields.items():
            _collect_pack_sites(field.type_declaration, path + [field_key], pack_sites,
                                next_active_type_names, under_generic_list)
        return

    if isinstance(type_, TUnion):
        if type_.name in active_type_names:
            return
        next_active_type_names = set(active_type_names)
        next_active_type_names.add(type_.name)
        for tag_key, tag_value in type_.tags.items():
            for field_key, field in tag_value.fields.items():
                _collect_pack_sites(field.type_declaration, path + [tag_key, field_key], pack_sites,
                                    next_active_type_names, under_generic_list)
        return


def construct_binary_encoding(telepact_schema: 'TelepactSchema') -> 'BinaryEncoding':
    from ..types.TUnion import TUnion

    all_keys: set[str] = set()
    pack_sites: list[list[object]] = []

    for key, value in telepact_schema.parsed.items():

        if key.endswith('.->') and isinstance(value, TUnion):
            result = value.tags['Ok_']
            all_keys.add('Ok_')
            for field_key, field in result.fields.items():
                all_keys.add(field_key)
                keys = trace_type(field.type_declaration)
                for key in keys:
                    all_keys.add(key)
                _collect_pack_sites(field.type_declaration, ['Ok_', field_key], pack_sites)

        elif key.startswith('fn.') and isinstance(value, TUnion):
            all_keys.add(key)
            args = value.tags[key]
            for field_key, field in args.fields.items():
                all_keys.add(field_key)
                keys = trace_type(field.type_declaration)
                for key in keys:
                    all_keys.add(key)
                _collect_pack_sites(field.type_declaration, [key, field_key], pack_sites)

    sorted_all_keys = sorted(all_keys)

    binary_encoding = {key: i for i, key in enumerate(sorted_all_keys)}
    final_string = "\n".join(sorted_all_keys)
    checksum = create_checksum(final_string)
    return BinaryEncoding(binary_encoding, checksum, pack_sites)
