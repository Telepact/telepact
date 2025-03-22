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

if TYPE_CHECKING:
    from ..types.TUnion import TUnion
    from ..types.TStruct import TStruct
    from ..types.TType import TType
    from ..types.TFieldDeclaration import TFieldDeclaration


def derive_possible_select(fn_name: str, result: 'TUnion') -> dict[str, object]:
    from ..types.TUnion import TUnion
    from ..types.TStruct import TStruct

    nested_types: dict[str, TType] = {}
    ok_fields: dict[str, TFieldDeclaration] = result.tags['Ok_'].fields

    ok_field_names = sorted(ok_fields.keys())

    find_nested_types(ok_fields, nested_types)

    possible_select: dict[str, object] = {}

    possible_select['->'] = {
        'Ok_': ok_field_names,
    }

    sorted_type_keys = sorted(nested_types.keys())
    for k in sorted_type_keys:
        v = nested_types[k]
        if isinstance(v, TUnion):
            union_select: dict[str, list[str]] = {}
            sorted_tag_keys = sorted(v.tags.keys())
            for c in sorted_tag_keys:
                typ = v.tags[c]
                selected_field_names: list[str] = sorted(typ.fields.keys())
                union_select[c] = selected_field_names

            possible_select[k] = union_select
        elif isinstance(v, TStruct):
            struct_select: list[str] = sorted(v.fields.keys())
            possible_select[k] = struct_select

    return possible_select


def find_nested_types(fields: dict[str, 'TFieldDeclaration'], nested_types: dict[str, 'TType']) -> None:
    from ..types.TUnion import TUnion
    from ..types.TStruct import TStruct

    for field in fields.values():
        typ = field.type_declaration.type
        if isinstance(typ, TUnion):
            nested_types[typ.name] = typ
            for c in typ.tags.values():
                find_nested_types(c.fields, nested_types)
        elif isinstance(typ, TStruct):
            nested_types[typ.name] = typ
            find_nested_types(typ.fields, nested_types)
