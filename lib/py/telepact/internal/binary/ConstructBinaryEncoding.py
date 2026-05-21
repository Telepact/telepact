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
    from ..types.TStruct import TStruct
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
        next_visited = set(visited_type_names)
        next_visited.add(type_declaration.type.name)
        for struct_field_key, struct_field in sorted(type_declaration.type.fields.items()):
            this_all_keys.append(struct_field_key)
            more_keys = trace_type(struct_field.type_declaration, next_visited)
            this_all_keys.extend(more_keys)
    elif isinstance(type_declaration.type, TUnion):
        if type_declaration.type.name in visited_type_names:
            return this_all_keys
        next_visited = set(visited_type_names)
        next_visited.add(type_declaration.type.name)
        for tag_key, tag_value in sorted(type_declaration.type.tags.items()):
            this_all_keys.append(tag_key)
            for struct_field_key, struct_field in sorted(tag_value.fields.items()):
                this_all_keys.append(struct_field_key)
                more_keys = trace_type(struct_field.type_declaration, next_visited)
                this_all_keys.extend(more_keys)

    return this_all_keys


def _build_nested_struct_header(type_declaration: 'TTypeDeclaration',
                                visited_type_names: set[str] | None = None) -> list[object] | None:
    from ..types.TStruct import TStruct

    if visited_type_names is None:
        visited_type_names = set()

    if not isinstance(type_declaration.type, TStruct):
        return None

    struct_type = type_declaration.type
    if struct_type.name in visited_type_names:
        return None

    next_visited = set(visited_type_names)
    next_visited.add(struct_type.name)

    nested_header: list[object] = []
    for field_key, field in sorted(struct_type.fields.items()):
        child_header = _build_nested_struct_header(field.type_declaration, next_visited)
        if child_header is None:
            nested_header.append(field_key)
        else:
            nested_header.append([field_key, *child_header])
    return nested_header


def _build_pack_header(struct_type: 'TStruct') -> list[object]:
    header: list[object] = [None]
    for field_key, field in sorted(struct_type.fields.items()):
        nested_header = _build_nested_struct_header(field.type_declaration, {struct_type.name})
        if nested_header is None:
            header.append(field_key)
        else:
            header.append([field_key, *nested_header])
    return header


def _collect_pack_sites(type_declaration: 'TTypeDeclaration', path: tuple[str, ...],
                        pack_sites: list[list[object]], visited_type_names: set[str] | None = None) -> None:
    from ..types.TArray import TArray
    from ..types.TObject import TObject
    from ..types.TStruct import TStruct
    from ..types.TUnion import TUnion

    if visited_type_names is None:
        visited_type_names = set()

    if isinstance(type_declaration.type, TObject):
        return

    if isinstance(type_declaration.type, TArray):
        item_type = type_declaration.type_parameters[0]
        if isinstance(item_type.type, TStruct):
            pack_sites.append([list(path), _build_pack_header(item_type.type)])
        return

    if isinstance(type_declaration.type, TStruct):
        struct_type = type_declaration.type
        if struct_type.name in visited_type_names:
            return
        next_visited = set(visited_type_names)
        next_visited.add(struct_type.name)
        for field_key, field in sorted(struct_type.fields.items()):
            _collect_pack_sites(field.type_declaration, (*path, field_key), pack_sites, next_visited)
        return

    if isinstance(type_declaration.type, TUnion):
        union_type = type_declaration.type
        if union_type.name in visited_type_names:
            return
        next_visited = set(visited_type_names)
        next_visited.add(union_type.name)
        for tag_key, tag_value in sorted(union_type.tags.items()):
            for field_key, field in sorted(tag_value.fields.items()):
                _collect_pack_sites(field.type_declaration, (*path, tag_key, field_key), pack_sites, next_visited)


def _stringify_pack_header_value(value: object) -> str:
    if isinstance(value, list):
        return '[' + ','.join(_stringify_pack_header_value(item) for item in value) + ']'
    if value is None:
        return 'null'
    return str(value)


def construct_binary_encoding(telepact_schema: 'TelepactSchema') -> 'BinaryEncoding':
    from ..types.TUnion import TUnion

    all_keys: set[str] = set()
    pack_sites: list[list[object]] = []

    for schema_key, value in telepact_schema.parsed.items():
        if schema_key.endswith('.->') and isinstance(value, TUnion):
            result = value.tags['Ok_']
            all_keys.add('Ok_')
            for field_key, field in sorted(result.fields.items()):
                all_keys.add(field_key)
                for nested_key in trace_type(field.type_declaration):
                    all_keys.add(nested_key)
                _collect_pack_sites(field.type_declaration, ('Ok_', field_key), pack_sites)
        elif schema_key.startswith('fn.') and isinstance(value, TUnion):
            all_keys.add(schema_key)
            args = value.tags[schema_key]
            for field_key, field in sorted(args.fields.items()):
                all_keys.add(field_key)
                for nested_key in trace_type(field.type_declaration):
                    all_keys.add(nested_key)
                _collect_pack_sites(field.type_declaration, (schema_key, field_key), pack_sites)

    sorted_all_keys = sorted(all_keys)
    pack_sites.sort(key=lambda item: '.'.join(item[0]))

    binary_encoding = {key: i for i, key in enumerate(sorted_all_keys)}
    final_string = '\n'.join(sorted_all_keys)
    if pack_sites:
        final_string += '\n--encp--\n' + '\n'.join(
            f"{'.'.join(path)}:{_stringify_pack_header_value(header)}"
            for path, header in pack_sites
        )
    checksum = create_checksum(final_string)
    return BinaryEncoding(binary_encoding, checksum, pack_sites)
