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

from ...internal.binary.BinaryEncoding import BinaryEncoding, BinaryPackHeader, BinaryPackSiteData
from ...internal.binary.CreateChecksum import create_checksum

if TYPE_CHECKING:
    from ...TelepactSchema import TelepactSchema
    from ..types.TFieldDeclaration import TFieldDeclaration
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
        child_type = type_declaration.type_parameters[0]
        this_all_keys.extend(trace_type(child_type, visited_type_names))
    elif isinstance(type_declaration.type, TObject):
        child_type = type_declaration.type_parameters[0]
        this_all_keys.extend(trace_type(child_type, visited_type_names))
    elif isinstance(type_declaration.type, TStruct):
        if type_declaration.type.name in visited_type_names:
            return this_all_keys
        visited_type_names = set(visited_type_names)
        visited_type_names.add(type_declaration.type.name)
        for struct_field_key, struct_field in type_declaration.type.fields.items():
            this_all_keys.append(struct_field_key)
            this_all_keys.extend(trace_type(struct_field.type_declaration, visited_type_names))
    elif isinstance(type_declaration.type, TUnion):
        if type_declaration.type.name in visited_type_names:
            return this_all_keys
        visited_type_names = set(visited_type_names)
        visited_type_names.add(type_declaration.type.name)
        for tag_key, tag_value in type_declaration.type.tags.items():
            this_all_keys.append(tag_key)
            for struct_field_key, struct_field in tag_value.fields.items():
                this_all_keys.append(struct_field_key)
                this_all_keys.extend(trace_type(struct_field.type_declaration, visited_type_names))

    return this_all_keys


def is_deterministic_packed_struct(type_declaration: 'TTypeDeclaration', visiting_type_names: set[str]) -> bool:
    from ..types.TArray import TArray
    from ..types.TObject import TObject
    from ..types.TStruct import TStruct
    from ..types.TUnion import TUnion

    if isinstance(type_declaration.type, TArray):
        child_type = type_declaration.type_parameters[0]
        return not isinstance(child_type.type, (TStruct, TUnion))

    if isinstance(type_declaration.type, TObject):
        return True

    if isinstance(type_declaration.type, TStruct):
        if type_declaration.type.name in visiting_type_names:
            return False
        next_visiting = set(visiting_type_names)
        next_visiting.add(type_declaration.type.name)
        return all(
            is_deterministic_packed_struct(field.type_declaration, next_visiting)
            for field in type_declaration.type.fields.values()
        )

    if isinstance(type_declaration.type, TUnion):
        if type_declaration.type.name in visiting_type_names:
            return False
        next_visiting = set(visiting_type_names)
        next_visiting.add(type_declaration.type.name)
        return all(
            is_deterministic_packed_struct(field.type_declaration, next_visiting)
            for tag_value in type_declaration.type.tags.values()
            for field in tag_value.fields.values()
        )

    return True


def get_encoded_key(binary_encoding: dict[str, int], key: str) -> int:
    return binary_encoding[key]


def build_nested_header(key: str, type_declaration: 'TTypeDeclaration', binary_encoding: dict[str, int]) -> int | BinaryPackHeader:
    from ..types.TStruct import TStruct
    from ..types.TUnion import TUnion

    encoded_key = get_encoded_key(binary_encoding, key)

    if isinstance(type_declaration.type, TStruct):
        header: BinaryPackHeader = [encoded_key]
        for field_key, field in type_declaration.type.fields.items():
            header.append(build_nested_header(field_key, field.type_declaration, binary_encoding))
        return header

    if isinstance(type_declaration.type, TUnion):
        header = [encoded_key]
        for tag_key, tag_value in type_declaration.type.tags.items():
            tag_header: BinaryPackHeader = [get_encoded_key(binary_encoding, tag_key)]
            for field_key, field in tag_value.fields.items():
                tag_header.append(build_nested_header(field_key, field.type_declaration, binary_encoding))
            header.append(tag_header)
        return header

    return encoded_key


def build_pack_header(struct_type: object, binary_encoding: dict[str, int]) -> BinaryPackHeader:
    header: BinaryPackHeader = [None]
    for field_key, field in struct_type.fields.items():
        header.append(build_nested_header(field_key, field.type_declaration, binary_encoding))
    return header


def collect_packed_sites(
    path: list[str],
    type_declaration: 'TTypeDeclaration',
    binary_encoding: dict[str, int],
    packed_sites: list[BinaryPackSiteData],
    visited_type_names: set[str] | None = None,
) -> None:
    from ..types.TArray import TArray
    from ..types.TObject import TObject
    from ..types.TStruct import TStruct
    from ..types.TUnion import TUnion

    if visited_type_names is None:
        visited_type_names = set()

    if isinstance(type_declaration.type, TArray):
        child_type = type_declaration.type_parameters[0]
        if isinstance(child_type.type, TStruct) and is_deterministic_packed_struct(child_type, set()):
            packed_sites.append((list(path), build_pack_header(child_type.type, binary_encoding)))
        return

    if isinstance(type_declaration.type, TObject):
        return

    if isinstance(type_declaration.type, TStruct):
        if type_declaration.type.name in visited_type_names:
            return
        next_visited = set(visited_type_names)
        next_visited.add(type_declaration.type.name)
        for field_key, field in type_declaration.type.fields.items():
            collect_packed_sites(path + [field_key], field.type_declaration, binary_encoding, packed_sites, next_visited)
        return

    if isinstance(type_declaration.type, TUnion):
        if type_declaration.type.name in visited_type_names:
            return
        next_visited = set(visited_type_names)
        next_visited.add(type_declaration.type.name)
        for tag_key, tag_value in type_declaration.type.tags.items():
            for field_key, field in tag_value.fields.items():
                collect_packed_sites(path + [tag_key, field_key], field.type_declaration, binary_encoding, packed_sites, next_visited)


def add_root_packed_sites(
    root_path: list[str],
    fields: dict[str, 'TFieldDeclaration'],
    binary_encoding: dict[str, int],
    packed_sites: list[BinaryPackSiteData],
) -> None:
    for field_key, field in fields.items():
        collect_packed_sites(root_path + [field_key], field.type_declaration, binary_encoding, packed_sites)


def construct_binary_encoding(telepact_schema: 'TelepactSchema') -> 'BinaryEncoding':
    from ..types.TUnion import TUnion

    all_keys: set[str] = set()

    for key, value in telepact_schema.parsed.items():
        if key.endswith('.->') and isinstance(value, TUnion):
            result = value.tags.get('Ok_')
            if result is None:
                continue
            all_keys.add('Ok_')
            for field_key, field in result.fields.items():
                all_keys.add(field_key)
                all_keys.update(trace_type(field.type_declaration))
        elif key.startswith('fn.') and isinstance(value, TUnion):
            all_keys.add(key)
            args = value.tags.get(key)
            if args is None:
                continue
            for field_key, field in args.fields.items():
                all_keys.add(field_key)
                all_keys.update(trace_type(field.type_declaration))

    sorted_all_keys = sorted(all_keys)
    binary_encoding = {key: i for i, key in enumerate(sorted_all_keys)}

    packed_sites: list[BinaryPackSiteData] = []
    for key, value in telepact_schema.parsed.items():
        if key.endswith('.->') and isinstance(value, TUnion):
            result = value.tags.get('Ok_')
            if result is not None:
                add_root_packed_sites(['Ok_'], result.fields, binary_encoding, packed_sites)
        elif key.startswith('fn.') and isinstance(value, TUnion):
            args = value.tags.get(key)
            if args is not None:
                add_root_packed_sites([key], args.fields, binary_encoding, packed_sites)

    final_string = "\n".join(sorted_all_keys)
    checksum = create_checksum(final_string)
    return BinaryEncoding(binary_encoding, checksum, packed_sites)
