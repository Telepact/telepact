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

from msgpack import ExtType

if TYPE_CHECKING:
    from ...internal.binary.BinaryEncoding import BinaryEncoding
    from ...internal.binary.BinaryEncoding import BinaryPackSite

PACKED_BYTE = 17
UNDEFINED_BYTE = 18


def _decode_key(key: object, binary_encoding: 'BinaryEncoding') -> str:
    if type(key) is str:
        return cast(str, key)
    try:
        return binary_encoding.decode_table[cast(int, key)]
    except (IndexError, TypeError) as exc:
        from ...internal.binary.BinaryEncodingMissing import BinaryEncodingMissing
        raise BinaryEncodingMissing(key) from exc


def _decode_plain_value(value: object, binary_encoding: 'BinaryEncoding') -> object:
    value_type = type(value)
    if value_type is dict:
        final_root: dict[str, object] = {}
        stack: list[tuple[str, object, object]] = [('dict', iter(cast(dict[object, object], value).items()), final_root)]

        while stack:
            frame_type, iterator, target = stack[-1]
            try:
                entry = next(cast(object, iterator))
            except StopIteration:
                stack.pop()
                continue

            if frame_type == 'dict':
                raw_key, item = cast(tuple[object, object], entry)
                decoded_key = _decode_key(raw_key, binary_encoding)
                item_type = type(item)
                if item_type is dict:
                    child_target: dict[str, object] = {}
                    cast(dict[str, object], target)[decoded_key] = child_target
                    stack.append(('dict', iter(cast(dict[object, object], item).items()), child_target))
                elif item_type is list:
                    child_target = [None] * len(cast(list[object], item))
                    cast(dict[str, object], target)[decoded_key] = child_target
                    stack.append(('list', enumerate(cast(list[object], item)), child_target))
                else:
                    cast(dict[str, object], target)[decoded_key] = item
            else:
                index, item = cast(tuple[int, object], entry)
                item_type = type(item)
                if item_type is dict:
                    child_target = {}
                    cast(list[object], target)[index] = child_target
                    stack.append(('dict', iter(cast(dict[object, object], item).items()), child_target))
                elif item_type is list:
                    child_target = [None] * len(cast(list[object], item))
                    cast(list[object], target)[index] = child_target
                    stack.append(('list', enumerate(cast(list[object], item)), child_target))
                else:
                    cast(list[object], target)[index] = item

        return final_root

    if value_type is list:
        final_root: list[object] = [None] * len(cast(list[object], value))
        stack = [('list', enumerate(cast(list[object], value)), final_root)]

        while stack:
            _, iterator, target = stack[-1]
            try:
                index, item = next(cast(object, iterator))
            except StopIteration:
                stack.pop()
                continue

            item_type = type(item)
            if item_type is dict:
                child_target = {}
                cast(list[object], target)[index] = child_target
                stack.append(('dict', iter(cast(dict[object, object], item).items()), child_target))
            elif item_type is list:
                child_target = [None] * len(cast(list[object], item))
                cast(list[object], target)[index] = child_target
                stack.append(('list', enumerate(cast(list[object], item)), child_target))
            else:
                cast(list[object], target)[index] = item

        return final_root

    return value


def _decode_packed_row(row: list[object], header: list[object], binary_encoding: 'BinaryEncoding') -> dict[str, object]:
    final_root: dict[str, object] = {}
    stack: list[tuple[list[object], list[object], dict[str, object], int]] = [(row, header, final_root, 1)]

    while stack:
        current_row, current_header, current_target, index = stack.pop()
        while index < len(current_header):
            header_item = current_header[index]
            row_index = index - 1
            if row_index >= len(current_row):
                break
            value = current_row[row_index]
            if type(value) is ExtType and cast(ExtType, value).code == UNDEFINED_BYTE:
                index += 1
                continue

            if isinstance(header_item, list):
                field_key = cast(str, header_item[0])
                if type(value) is not list:
                    raise TypeError("packed nested row value must be a list")
                nested_target: dict[str, object] = {}
                current_target[field_key] = nested_target
                stack.append((current_row, current_header, current_target, index + 1))
                current_row = cast(list[object], value)
                current_header = header_item
                current_target = nested_target
                index = 1
                continue

            value_type = type(value)
            if value_type is dict or value_type is list:
                current_target[cast(str, header_item)] = _decode_plain_value(value, binary_encoding)
            else:
                current_target[cast(str, header_item)] = value
            index += 1

    return final_root


def _decode_packed_list(value: list[object], pack_site: 'BinaryPackSite',
                        binary_encoding: 'BinaryEncoding') -> list[object]:
    if len(value) < 2:
        return []
    first_item = value[0]
    if type(first_item) is not ExtType or cast(ExtType, first_item).code != PACKED_BYTE:
        return cast(list[object], _decode_plain_value(value, binary_encoding))

    final_list: list[object] = []
    try:
        for row in value[2:]:
            if type(row) is not list:
                raise TypeError("packed row must be a list")
            final_list.append(_decode_packed_row(cast(list[object], row), pack_site.header, binary_encoding))
        return final_list
    except TypeError:
        return cast(list[object], _decode_plain_value(value, binary_encoding))


def decode_body(encoded_message_body: dict[object, object], binary_encoder: 'BinaryEncoding',
                packed: bool = False) -> dict[str, object]:
    pack_sites_by_encoded_path = binary_encoder.pack_sites_by_encoded_path if packed else {}
    final_root: dict[str, object] = {}
    stack: list[tuple[str, object, object, tuple[int, ...], bool]] = [
        ('dict', iter(encoded_message_body.items()), final_root, tuple(), True)
    ]

    while stack:
        frame_type, iterator, target, path, track_paths = stack[-1]
        try:
            entry = next(cast(object, iterator))
        except StopIteration:
            stack.pop()
            continue

        if frame_type == 'dict':
            raw_key, item = cast(tuple[object, object], entry)
            decoded_key = _decode_key(raw_key, binary_encoder)
            next_path = (*path, cast(int, raw_key)) if track_paths and type(raw_key) is int else tuple()
            item_type = type(item)
            if item_type is list and track_paths and next_path in pack_sites_by_encoded_path:
                cast(dict[str, object], target)[decoded_key] = _decode_packed_list(
                    cast(list[object], item),
                    pack_sites_by_encoded_path[next_path],
                    binary_encoder,
                )
            elif item_type is dict:
                child_target = {}
                cast(dict[str, object], target)[decoded_key] = child_target
                stack.append(('dict', iter(cast(dict[object, object], item).items()), child_target, next_path, track_paths))
            elif item_type is list:
                child_target = [None] * len(cast(list[object], item))
                cast(dict[str, object], target)[decoded_key] = child_target
                stack.append(('list', enumerate(cast(list[object], item)), child_target, tuple(), False))
            else:
                cast(dict[str, object], target)[decoded_key] = item
        else:
            index, item = cast(tuple[int, object], entry)
            item_type = type(item)
            if item_type is dict:
                child_target = {}
                cast(list[object], target)[index] = child_target
                stack.append(('dict', iter(cast(dict[object, object], item).items()), child_target, tuple(), False))
            elif item_type is list:
                child_target = [None] * len(cast(list[object], item))
                cast(list[object], target)[index] = child_target
                stack.append(('list', enumerate(cast(list[object], item)), child_target, tuple(), False))
            else:
                cast(list[object], target)[index] = item

    return final_root
