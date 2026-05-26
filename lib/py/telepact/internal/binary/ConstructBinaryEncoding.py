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
    from ..types.TStruct import TStruct


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


def construct_binary_encoding(telepact_schema: 'TelepactSchema') -> 'BinaryEncoding':
    from ..types.TUnion import TUnion

    all_keys: set[str] = set()

    for key, value in telepact_schema.parsed.items():

        if key.endswith('.->') and isinstance(value, TUnion):
            result = value.tags['Ok_']
            all_keys.add('Ok_')
            for field_key, field in result.fields.items():
                all_keys.add(field_key)
                keys = trace_type(field.type_declaration)
                for key in keys:
                    all_keys.add(key)

        elif key.startswith('fn.') and isinstance(value, TUnion):
            all_keys.add(key)
            args = value.tags[key]
            for field_key, field in args.fields.items():
                all_keys.add(field_key)
                keys = trace_type(field.type_declaration)
                for key in keys:
                    all_keys.add(key)

    sorted_all_keys = sorted(all_keys)

    binary_encoding = {key: i for i, key in enumerate(sorted_all_keys)}
    final_string = "\n".join(sorted_all_keys)
    checksum = create_checksum(final_string)
    pack_encoding = construct_binary_pack_encoding(telepact_schema)
    return BinaryEncoding(binary_encoding, checksum, pack_encoding)


def construct_binary_pack_encoding(telepact_schema: 'TelepactSchema') -> dict[str, object]:
    from ..types.TUnion import TUnion

    pack_encoding: dict[str, object] = {}

    for key, value in telepact_schema.parsed.items():
        if not key.startswith("fn.") or key.endswith(".->") or not isinstance(value, TUnion):
            continue

        function_pack_encoding: dict[str, object] = {}

        request_struct = value.tags.get(key)
        if request_struct is not None:
            request_tree: dict[str, object] = {}
            _collect_pack_sites_in_struct(request_struct, [key], request_tree, set())
            if request_tree:
                function_pack_encoding[key] = request_tree[key]

        result_union = telepact_schema.parsed.get(key + ".->")
        if isinstance(result_union, TUnion):
            response_tree: dict[str, object] = {}
            ok_struct = result_union.tags.get("Ok_")
            if ok_struct is not None:
                _collect_pack_sites_in_struct(ok_struct, ["Ok_"], response_tree, set())
            if response_tree:
                function_pack_encoding["->"] = response_tree

        if function_pack_encoding:
            pack_encoding[key] = function_pack_encoding

    return pack_encoding


def _collect_pack_sites_in_union(
    union: object,
    path: list[str],
    tree: dict[str, object],
    visited: set[str],
) -> None:
    from ..types.TUnion import TUnion

    if not isinstance(union, TUnion):
        return

    if union.name in visited:
        return

    next_visited = set(visited)
    next_visited.add(union.name)

    for tag_key, tag_struct in union.tags.items():
        _collect_pack_sites_in_struct(tag_struct, path + [tag_key], tree, next_visited)


def _collect_pack_sites_in_struct(
    struct: 'TStruct',
    path: list[str],
    tree: dict[str, object],
    visited: set[str],
) -> None:
    if struct.name in visited:
        return

    next_visited = set(visited)
    next_visited.add(struct.name)

    for field_key, field in struct.fields.items():
        _collect_pack_sites_in_type_declaration(
            field.type_declaration,
            path + [field_key],
            tree,
            next_visited,
        )


def _collect_pack_sites_in_type_declaration(
    type_declaration: 'TTypeDeclaration',
    path: list[str],
    tree: dict[str, object],
    visited: set[str],
) -> None:
    from ..types.TArray import TArray
    from ..types.TObject import TObject
    from ..types.TStruct import TStruct
    from ..types.TUnion import TUnion

    type_ = type_declaration.type

    if isinstance(type_, TArray):
        element_type_declaration = type_declaration.type_parameters[0]
        element_type = element_type_declaration.type
        if isinstance(element_type, TStruct):
            _insert_pack_site(tree, path, _build_pack_header(element_type, set()))
        return

    if isinstance(type_, TObject):
        return

    if isinstance(type_, TStruct):
        _collect_pack_sites_in_struct(type_, path, tree, visited)
        return

    if isinstance(type_, TUnion):
        _collect_pack_sites_in_union(type_, path, tree, visited)


def _build_pack_header(struct: 'TStruct', visited: set[str]) -> list[object]:
    from ..types.TStruct import TStruct

    header: list[object] = [None]

    if struct.name in visited:
        return header

    next_visited = set(visited)
    next_visited.add(struct.name)

    for field_key, field in struct.fields.items():
        field_type = field.type_declaration.type
        if isinstance(field_type, TStruct) and field_type.name not in next_visited:
            nested_header = _build_pack_header(field_type, next_visited)
            nested_header[0] = field_key
            header.append(nested_header)
        else:
            header.append(field_key)

    return header


def _insert_pack_site(tree: dict[str, object], path: list[str], header: list[object]) -> None:
    current = tree
    for key in path[:-1]:
        next_value = current.get(key)
        if not isinstance(next_value, dict):
            next_value = {}
            current[key] = next_value
        current = next_value
    current[path[-1]] = header
