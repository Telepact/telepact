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

if TYPE_CHECKING:
    from ...internal.binary.BinaryEncoding import BinaryEncoding
    from ...internal.binary.BinaryEncoding import BinaryPackSite

from msgpack import ExtType

PACKED_BYTE = 17
PACKED_EXT = ExtType(PACKED_BYTE, b'')
UNDEFINED_BYTE = 18
UNDEFINED_EXT = ExtType(UNDEFINED_BYTE, b'')


def _encode_plain_value(value: object, binary_encoding: 'BinaryEncoding') -> object:
    encode_map = binary_encoding.encode_map
    value_type = type(value)

    if value_type is dict:
        root = cast(dict[object, object], value)
        final_root: dict[object, object] = {}
        stack: list[tuple[str, object, object]] = [('dict', iter(root.items()), final_root)]

        while stack:
            frame_type, iterator, target = stack[-1]
            try:
                entry = next(cast(object, iterator))
            except StopIteration:
                stack.pop()
                continue

            if frame_type == 'dict':
                key, item = cast(tuple[object, object], entry)
                encoded_key = encode_map.get(key, key)
                item_type = type(item)
                if item_type is dict:
                    child_target: dict[object, object] = {}
                    cast(dict[object, object], target)[encoded_key] = child_target
                    stack.append(('dict', iter(cast(dict[object, object], item).items()), child_target))
                elif item_type is list:
                    child_target = [None] * len(cast(list[object], item))
                    cast(dict[object, object], target)[encoded_key] = child_target
                    stack.append(('list', enumerate(cast(list[object], item)), child_target))
                else:
                    cast(dict[object, object], target)[encoded_key] = item
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
        root = cast(list[object], value)
        final_root: list[object] = [None] * len(root)
        stack = [('list', enumerate(root), final_root)]

        while stack:
            frame_type, iterator, target = stack[-1]
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


def _encode_packed_row(item: dict[object, object], header: list[object], binary_encoding: 'BinaryEncoding') -> list[object]:
    row_root: list[object] = [UNDEFINED_EXT] * (len(header) - 1)
    stack: list[tuple[dict[object, object], list[object], list[object], int]] = [(item, header, row_root, 1)]

    while stack:
        source, current_header, current_row, index = stack.pop()
        while index < len(current_header):
            header_item = current_header[index]
            row_index = index - 1
            if isinstance(header_item, list):
                field_key = cast(object, header_item[0])
                if field_key not in source:
                    index += 1
                    continue
                value = source[field_key]
                if type(value) is not dict:
                    raise TypeError("packed nested struct value must be a map")
                nested_row: list[object] = [UNDEFINED_EXT] * (len(header_item) - 1)
                current_row[row_index] = nested_row
                stack.append((source, current_header, current_row, index + 1))
                source = cast(dict[object, object], value)
                current_header = header_item
                current_row = nested_row
                index = 1
                continue

            if header_item in source:
                value = source[header_item]
                value_type = type(value)
                if value_type is dict or value_type is list:
                    current_row[row_index] = _encode_plain_value(value, binary_encoding)
                else:
                    current_row[row_index] = value
            index += 1

    return row_root


def _encode_packed_list(values: list[object], pack_site: 'BinaryPackSite',
                        binary_encoding: 'BinaryEncoding') -> list[object]:
    packed_list: list[object] = [PACKED_EXT, cast(list[object], pack_site.encoded_header)]
    try:
        for item in values:
            if type(item) is not dict:
                raise TypeError("packed list items must be maps")
            packed_list.append(_encode_packed_row(cast(dict[object, object], item), pack_site.header, binary_encoding))
        return packed_list
    except TypeError:
        return cast(list[object], _encode_plain_value(values, binary_encoding))


def encode_body(message_body: dict[str, object], binary_encoding: 'BinaryEncoding',
                packed: bool = False) -> dict[object, object]:
    encode_map = binary_encoding.encode_map
    pack_sites_by_path = binary_encoding.pack_sites_by_path if packed else {}
    final_root: dict[object, object] = {}
    stack: list[tuple[str, object, object, tuple[str, ...], bool]] = [
        ('dict', iter(message_body.items()), final_root, tuple(), True)
    ]

    while stack:
        frame_type, iterator, target, path, track_paths = stack[-1]
        try:
            entry = next(cast(object, iterator))
        except StopIteration:
            stack.pop()
            continue

        if frame_type == 'dict':
            key, item = cast(tuple[str, object], entry)
            encoded_key = encode_map.get(key, key)
            next_path = (*path, key) if track_paths else tuple()
            item_type = type(item)
            if item_type is list:
                pack_site = pack_sites_by_path.get(next_path)
                if pack_site is not None:
                    cast(dict[object, object], target)[encoded_key] = _encode_packed_list(
                        cast(list[object], item), pack_site, binary_encoding
                    )
                else:
                    child_target = [None] * len(cast(list[object], item))
                    cast(dict[object, object], target)[encoded_key] = child_target
                    stack.append(('list', enumerate(cast(list[object], item)), child_target, tuple(), False))
            elif item_type is dict:
                child_target = {}
                cast(dict[object, object], target)[encoded_key] = child_target
                stack.append(('dict', iter(cast(dict[object, object], item).items()), child_target, next_path, track_paths))
            else:
                cast(dict[object, object], target)[encoded_key] = item
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
