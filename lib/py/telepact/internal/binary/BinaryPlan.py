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

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from ...internal.binary.BinaryEncodingMissing import BinaryEncodingMissing
from ...internal.binary.DecodeKeys import decode_keys
from ...internal.binary.EncodeKeys import encode_keys
from ...internal.binary.Pack import pack
from ...internal.binary.PackBody import pack_body
from ...internal.binary.PackList import PACKED_EXT
from ...internal.binary.PackMap import UNDEFINED_EXT
from ...internal.binary.Unpack import unpack
from ...internal.binary.UnpackMap import unpack_map

if TYPE_CHECKING:
    from ...internal.binary.BinaryEncoding import BinaryEncoding
    from ..types.TTypeDeclaration import TTypeDeclaration


_PLAN_VALUE = "v"
_PLAN_DYNAMIC = "d"
_PLAN_ARRAY = "a"
_PLAN_STRUCT = "s"
_PLAN_UNION = "u"


@dataclass(slots=True)
class ValuePlan:
    kind: str = _PLAN_VALUE


@dataclass(slots=True)
class DynamicPlan:
    kind: str = _PLAN_DYNAMIC


@dataclass(slots=True)
class ArrayPlan:
    item_plan: object
    kind: str = _PLAN_ARRAY


@dataclass(slots=True)
class StructFieldPlan:
    name: str
    field_id: int
    plan: object


@dataclass(slots=True)
class StructPlan:
    fields: list[StructFieldPlan]
    fields_by_name: dict[str, StructFieldPlan]
    fields_by_id: dict[int, StructFieldPlan]
    packable: bool
    packed_header: list[object]
    kind: str = _PLAN_STRUCT


@dataclass(slots=True)
class UnionTagPlan:
    tag_name: str
    tag_id: int
    plan: StructPlan


@dataclass(slots=True)
class UnionPlan:
    tags_by_name: dict[str, UnionTagPlan]
    tags_by_id: dict[int, UnionTagPlan]
    kind: str = _PLAN_UNION


def compile_type_descriptor(
    type_declaration: "TTypeDeclaration",
    encode_map: dict[str, int],
    visited_type_names: set[str] | None = None,
) -> dict[str, object]:
    from ..types.TArray import TArray
    from ..types.TObject import TObject
    from ..types.TStruct import TStruct
    from ..types.TUnion import TUnion

    if visited_type_names is None:
        visited_type_names = set()

    type_value = type_declaration.type

    if isinstance(type_value, TArray):
        return {
            "t": _PLAN_ARRAY,
            "i": compile_type_descriptor(type_declaration.type_parameters[0], encode_map, visited_type_names),
        }

    if isinstance(type_value, TObject):
        return {"t": _PLAN_DYNAMIC}

    if isinstance(type_value, TStruct):
        if type_value.name in visited_type_names:
            return {"t": _PLAN_DYNAMIC}

        next_visited = set(visited_type_names)
        next_visited.add(type_value.name)
        return {
            "t": _PLAN_STRUCT,
            "f": [
                [
                    encode_map[field_name],
                    compile_type_descriptor(field.type_declaration, encode_map, next_visited),
                ]
                for field_name, field in type_value.fields.items()
            ],
        }

    if isinstance(type_value, TUnion):
        if type_value.name in visited_type_names:
            return {"t": _PLAN_DYNAMIC}

        next_visited = set(visited_type_names)
        next_visited.add(type_value.name)
        return {
            "t": _PLAN_UNION,
            "g": [
                [
                    encode_map[tag_name],
                    {
                        "t": _PLAN_STRUCT,
                        "f": [
                            [
                                encode_map[field_name],
                                compile_type_descriptor(field.type_declaration, encode_map, next_visited),
                            ]
                            for field_name, field in tag_struct.fields.items()
                        ],
                    },
                ]
                for tag_name, tag_struct in type_value.tags.items()
            ],
        }

    return {"t": _PLAN_VALUE}


def compile_plan_descriptor(descriptor: dict[str, object], binary_encoding: "BinaryEncoding") -> object:
    tag = cast(str, descriptor["t"])

    if tag == _PLAN_VALUE:
        return ValuePlan()

    if tag == _PLAN_DYNAMIC:
        return DynamicPlan()

    if tag == _PLAN_ARRAY:
        return ArrayPlan(
            compile_plan_descriptor(cast(dict[str, object], descriptor["i"]), binary_encoding),
        )

    if tag == _PLAN_STRUCT:
        fields: list[StructFieldPlan] = []
        fields_by_name: dict[str, StructFieldPlan] = {}
        fields_by_id: dict[int, StructFieldPlan] = {}

        for field_entry in cast(list[list[object]], descriptor["f"]):
            field_id = cast(int, field_entry[0])
            field_name = binary_encoding.decode_map[field_id]
            field_plan = StructFieldPlan(
                field_name,
                field_id,
                compile_plan_descriptor(cast(dict[str, object], field_entry[1]), binary_encoding),
            )
            fields.append(field_plan)
            fields_by_name[field_name] = field_plan
            fields_by_id[field_id] = field_plan

        packable = all(_plan_can_be_row_value(field.plan) for field in fields)
        packed_header = [None, *[field.field_id for field in fields]]
        return StructPlan(fields, fields_by_name, fields_by_id, packable, packed_header)

    if tag == _PLAN_UNION:
        tags_by_name: dict[str, UnionTagPlan] = {}
        tags_by_id: dict[int, UnionTagPlan] = {}

        for tag_entry in cast(list[list[object]], descriptor["g"]):
            tag_id = cast(int, tag_entry[0])
            tag_name = binary_encoding.decode_map[tag_id]
            compiled_tag = UnionTagPlan(
                tag_name,
                tag_id,
                cast(StructPlan, compile_plan_descriptor(cast(dict[str, object], tag_entry[1]), binary_encoding)),
            )
            tags_by_name[tag_name] = compiled_tag
            tags_by_id[tag_id] = compiled_tag

        return UnionPlan(tags_by_name, tags_by_id)

    return DynamicPlan()


def compile_plan_map(plan_entries: list[list[object]], binary_encoding: "BinaryEncoding") -> dict[int, object]:
    compiled: dict[int, object] = {}
    for root_id, descriptor in plan_entries:
        compiled[cast(int, root_id)] = compile_plan_descriptor(cast(dict[str, object], descriptor), binary_encoding)
    return compiled


def encode_request_body(
    message_body: dict[str, object],
    binary_encoding: "BinaryEncoding",
    pack_enabled: bool,
) -> dict[object, object]:
    if len(message_body) != 1:
        encoded = cast(dict[object, object], encode_keys(message_body, binary_encoding))
        return pack_body(encoded) if pack_enabled else encoded

    root_name, payload = next(iter(message_body.items()))
    root_id = binary_encoding.encode_map.get(root_name)
    plan = binary_encoding.request_plans_by_root_id.get(root_id) if root_id is not None else None

    if root_id is None or plan is None:
        encoded = cast(dict[object, object], encode_keys(message_body, binary_encoding))
        return pack_body(encoded) if pack_enabled else encoded

    encoded_body = {
        root_id: _encode_value(payload, plan, binary_encoding, pack_enabled),
    }
    return pack_body(encoded_body) if pack_enabled else encoded_body


def encode_response_body(
    message_body: dict[str, object],
    binary_encoding: "BinaryEncoding",
    function_id: int | None,
    pack_enabled: bool,
) -> dict[object, object]:
    if len(message_body) != 1 or function_id is None:
        encoded = cast(dict[object, object], encode_keys(message_body, binary_encoding))
        return pack_body(encoded) if pack_enabled else encoded

    root_name, payload = next(iter(message_body.items()))
    if root_name != "Ok_":
        encoded = cast(dict[object, object], encode_keys(message_body, binary_encoding))
        return pack_body(encoded) if pack_enabled else encoded

    plan = binary_encoding.response_plans_by_function_id.get(function_id)
    ok_id = binary_encoding.encode_map.get("Ok_")
    if plan is None or ok_id is None:
        encoded = cast(dict[object, object], encode_keys(message_body, binary_encoding))
        return pack_body(encoded) if pack_enabled else encoded

    encoded_body = {
        ok_id: _encode_value(payload, plan, binary_encoding, pack_enabled),
    }
    return pack_body(encoded_body) if pack_enabled else encoded_body


def decode_request_body(
    encoded_message_body: dict[object, object],
    binary_encoding: "BinaryEncoding",
    pack_enabled: bool,
) -> dict[str, object]:
    if len(encoded_message_body) != 1:
        decoded_input = unpack(encoded_message_body) if pack_enabled else encoded_message_body
        return cast(dict[str, object], decode_keys(decoded_input, binary_encoding))

    root_id, payload = next(iter(encoded_message_body.items()))
    if type(root_id) is not int:
        decoded_input = unpack(encoded_message_body) if pack_enabled else encoded_message_body
        return cast(dict[str, object], decode_keys(decoded_input, binary_encoding))

    root_id_int = cast(int, root_id)
    root_name = binary_encoding.decode_map.get(root_id_int)
    plan = binary_encoding.request_plans_by_root_id.get(root_id_int)

    if root_name is None or plan is None:
        decoded_input = unpack(encoded_message_body) if pack_enabled else encoded_message_body
        return cast(dict[str, object], decode_keys(decoded_input, binary_encoding))

    return {
        root_name: cast(object, _decode_value(payload, plan, binary_encoding, pack_enabled)),
    }


def decode_response_body(
    encoded_message_body: dict[object, object],
    binary_encoding: "BinaryEncoding",
    function_id: int | None,
    pack_enabled: bool,
) -> dict[str, object]:
    if len(encoded_message_body) != 1 or function_id is None:
        decoded_input = unpack(encoded_message_body) if pack_enabled else encoded_message_body
        return cast(dict[str, object], decode_keys(decoded_input, binary_encoding))

    ok_id = binary_encoding.encode_map.get("Ok_")
    root_id, payload = next(iter(encoded_message_body.items()))
    if type(root_id) is not int or root_id != ok_id:
        decoded_input = unpack(encoded_message_body) if pack_enabled else encoded_message_body
        return cast(dict[str, object], decode_keys(decoded_input, binary_encoding))

    plan = binary_encoding.response_plans_by_function_id.get(function_id)
    if plan is None:
        decoded_input = unpack(encoded_message_body) if pack_enabled else encoded_message_body
        return cast(dict[str, object], decode_keys(decoded_input, binary_encoding))

    return {
        "Ok_": cast(object, _decode_value(payload, plan, binary_encoding, pack_enabled)),
    }


def _encode_value(value: object, plan: object, binary_encoding: "BinaryEncoding", pack_enabled: bool) -> object:
    if isinstance(plan, ValuePlan):
        return value

    if isinstance(plan, DynamicPlan):
        return encode_keys(value, binary_encoding)

    if isinstance(plan, ArrayPlan):
        if type(value) is not list:
            return encode_keys(value, binary_encoding)

        array_value = cast(list[object], value)
        if pack_enabled and isinstance(plan.item_plan, StructPlan) and plan.item_plan.packable:
            packed = _encode_packable_struct_array(array_value, cast(StructPlan, plan.item_plan), binary_encoding, pack_enabled)
            if packed is not None:
                return packed

        return [
            _encode_value(item, plan.item_plan, binary_encoding, pack_enabled)
            for item in array_value
        ]

    if isinstance(plan, StructPlan):
        if type(value) is not dict:
            return encode_keys(value, binary_encoding)

        given = cast(dict[object, object], value)
        encoded: dict[object, object] = {}
        for key, item in given.items():
            if type(key) is not str:
                encoded[key] = _encode_value(item, DynamicPlan(), binary_encoding, pack_enabled)
                continue

            field = plan.fields_by_name.get(cast(str, key))
            if field is None:
                encoded[binary_encoding.encode_map.get(cast(str, key), key)] = encode_keys(item, binary_encoding)
            else:
                encoded[field.field_id] = _encode_value(item, field.plan, binary_encoding, pack_enabled)

        return encoded

    if isinstance(plan, UnionPlan):
        if type(value) is not dict:
            return encode_keys(value, binary_encoding)

        given = cast(dict[object, object], value)
        if len(given) != 1:
            return encode_keys(value, binary_encoding)

        tag_name, tag_value = next(iter(given.items()))
        if type(tag_name) is not str:
            return encode_keys(value, binary_encoding)

        tag = plan.tags_by_name.get(cast(str, tag_name))
        if tag is None:
            return encode_keys(value, binary_encoding)

        return {
            tag.tag_id: cast(object, _encode_value(tag_value, tag.plan, binary_encoding, pack_enabled)),
        }

    return encode_keys(value, binary_encoding)


def _decode_value(value: object, plan: object, binary_encoding: "BinaryEncoding", pack_enabled: bool) -> object:
    if isinstance(plan, ValuePlan):
        return value

    if isinstance(plan, DynamicPlan):
        decoded_input = unpack(value) if pack_enabled else value
        return decode_keys(decoded_input, binary_encoding)

    if isinstance(plan, ArrayPlan):
        if type(value) is not list:
            decoded_input = unpack(value) if pack_enabled else value
            return decode_keys(decoded_input, binary_encoding)

        list_value = cast(list[object], value)
        if pack_enabled and isinstance(plan.item_plan, StructPlan) and plan.item_plan.packable:
            decoded_packed = _decode_packable_struct_array(list_value, cast(StructPlan, plan.item_plan), binary_encoding, pack_enabled)
            if decoded_packed is not None:
                return decoded_packed

        return [
            _decode_value(item, plan.item_plan, binary_encoding, pack_enabled)
            for item in list_value
        ]

    if isinstance(plan, StructPlan):
        if type(value) is not dict:
            decoded_input = unpack(value) if pack_enabled else value
            return decode_keys(decoded_input, binary_encoding)

        given = cast(dict[object, object], value)
        decoded: dict[str, object] = {}
        for key, item in given.items():
            if type(key) is str:
                decoded_key = cast(str, key)
                field = plan.fields_by_name.get(decoded_key)
                if field is None:
                    decoded[decoded_key] = _decode_value(item, DynamicPlan(), binary_encoding, pack_enabled)
                else:
                    decoded[decoded_key] = _decode_value(item, field.plan, binary_encoding, pack_enabled)
                continue

            field = plan.fields_by_id.get(cast(int, key))
            if field is None:
                decoded_key = binary_encoding.decode_map.get(cast(int, key))
                if decoded_key is None:
                    raise BinaryEncodingMissing(key)
                decoded[decoded_key] = decode_keys(unpack(item) if pack_enabled else item, binary_encoding)
            else:
                decoded[field.name] = _decode_value(item, field.plan, binary_encoding, pack_enabled)

        return decoded

    if isinstance(plan, UnionPlan):
        if type(value) is not dict:
            decoded_input = unpack(value) if pack_enabled else value
            return decode_keys(decoded_input, binary_encoding)

        given = cast(dict[object, object], value)
        if len(given) != 1:
            decoded_input = unpack(value) if pack_enabled else value
            return decode_keys(decoded_input, binary_encoding)

        tag_key, tag_value = next(iter(given.items()))
        if type(tag_key) is str:
            tag = plan.tags_by_name.get(cast(str, tag_key))
            if tag is None:
                decoded_input = unpack(value) if pack_enabled else value
                return decode_keys(decoded_input, binary_encoding)
            return {tag.tag_name: cast(object, _decode_value(tag_value, tag.plan, binary_encoding, pack_enabled))}

        tag = plan.tags_by_id.get(cast(int, tag_key))
        if tag is None:
            decoded_key = binary_encoding.decode_map.get(cast(int, tag_key))
            if decoded_key is None:
                raise BinaryEncodingMissing(tag_key)
            return {decoded_key: cast(object, decode_keys(unpack(tag_value) if pack_enabled else tag_value, binary_encoding))}

        return {tag.tag_name: cast(object, _decode_value(tag_value, tag.plan, binary_encoding, pack_enabled))}

    decoded_input = unpack(value) if pack_enabled else value
    return decode_keys(decoded_input, binary_encoding)


def _encode_packable_struct_array(
    array_value: list[object],
    struct_plan: StructPlan,
    binary_encoding: "BinaryEncoding",
    pack_enabled: bool,
) -> list[object] | None:
    packed_list: list[object] = [PACKED_EXT, list(struct_plan.packed_header)]
    for item in array_value:
        if type(item) is not dict:
            return None

        row = [UNDEFINED_EXT] * len(struct_plan.fields)
        item_dict = cast(dict[object, object], item)

        for key in item_dict.keys():
            if type(key) is not str or cast(str, key) not in struct_plan.fields_by_name:
                return None

        for index, field in enumerate(struct_plan.fields):
            if field.name not in item_dict:
                continue
            encoded_value = _encode_value(item_dict[field.name], field.plan, binary_encoding, pack_enabled)
            if type(encoded_value) is dict:
                return None
            row[index] = encoded_value

        packed_list.append(row)

    return packed_list


def _decode_packable_struct_array(
    list_value: list[object],
    struct_plan: StructPlan,
    binary_encoding: "BinaryEncoding",
    pack_enabled: bool,
) -> list[object] | None:
    if not list_value:
        return list_value

    first_item = list_value[0]
    if first_item != PACKED_EXT:
        return None

    if len(list_value) < 2 or cast(list[object], list_value[1]) != struct_plan.packed_header:
        return None

    decoded_list: list[object] = []
    for index in range(2, len(list_value)):
        row = cast(list[object], list_value[index])
        decoded_row: dict[str, object] = {}
        for field_index, field in enumerate(struct_plan.fields):
            if field_index >= len(row):
                continue

            cell = row[field_index]
            if cell == UNDEFINED_EXT:
                continue

            decoded_row[field.name] = _decode_value(cell, field.plan, binary_encoding, pack_enabled)
        decoded_list.append(decoded_row)

    return decoded_list


def _plan_can_be_row_value(plan: object) -> bool:
    if isinstance(plan, (StructPlan, UnionPlan, DynamicPlan)):
        return False
    return True
