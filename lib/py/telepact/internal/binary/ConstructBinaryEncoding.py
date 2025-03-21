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

from typing import List, Dict, Tuple, Set, Union
from typing import TYPE_CHECKING


from ...internal.binary.BinaryEncoding import BinaryEncoding
from ...internal.binary.CreateChecksum import create_checksum

if TYPE_CHECKING:
    from ...TelepactSchema import TelepactSchema
    from ..types.VTypeDeclaration import VTypeDeclaration


def trace_type(type_declaration: 'VTypeDeclaration') -> list[str]:
    from ..types.VArray import VArray
    from ..types.VObject import VObject
    from ..types.VStruct import VStruct
    from ..types.VUnion import VUnion

    this_all_keys: list[str] = []

    if isinstance(type_declaration.type, VArray):
        these_keys2 = trace_type(type_declaration.type_parameters[0])
        this_all_keys.extend(these_keys2)
    elif isinstance(type_declaration.type, VObject):
        these_keys2 = trace_type(type_declaration.type_parameters[0])
        this_all_keys.extend(these_keys2)
    elif isinstance(type_declaration.type, VStruct):
        struct_fields = type_declaration.type.fields
        for struct_field_key, struct_field in struct_fields.items():
            this_all_keys.append(struct_field_key)
            more_keys = trace_type(struct_field.type_declaration)
            this_all_keys.extend(more_keys)
    elif isinstance(type_declaration.type, VUnion):
        union_tags = type_declaration.type.tags
        for tag_key, tag_value in union_tags.items():
            this_all_keys.append(tag_key)
            struct_fields = tag_value.fields
            for struct_field_key, struct_field in struct_fields.items():
                this_all_keys.append(struct_field_key)
                more_keys = trace_type(struct_field.type_declaration)
                this_all_keys.extend(more_keys)

    return this_all_keys


def construct_binary_encoding(telepact_schema: 'TelepactSchema') -> 'BinaryEncoding':
    from ..types.VTypeDeclaration import VTypeDeclaration
    from ..types.VFn import VFn

    all_keys: set[str] = set()

    functions: list[Tuple[str, VFn]] = []

    for key, value in telepact_schema.parsed.items():
        if isinstance(value, VFn):
            functions.append((key, value))

    for key, value in functions:
        all_keys.add(key)
        args = value.call.tags[key]
        for field_key, field in args.fields.items():
            all_keys.add(field_key)
            keys = trace_type(field.type_declaration)
            for key in keys:
                all_keys.add(key)

        result = value.result.tags['Ok_']
        all_keys.add('Ok_')
        for field_key, field in result.fields.items():
            all_keys.add(field_key)
            keys = trace_type(field.type_declaration)
            for key in keys:
                all_keys.add(key)

    sorted_all_keys = sorted(all_keys)

    binary_encoding = {key: i for i, key in enumerate(sorted_all_keys)}
    final_string = "\n".join(sorted_all_keys)
    checksum = create_checksum(final_string)
    return BinaryEncoding(binary_encoding, checksum)
