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

from ...internal.binary.BinaryEncodingMissing import BinaryEncodingMissing

if TYPE_CHECKING:
    from ...internal.binary.BinaryEncoding import BinaryEncoding


def _decode_list(items: list[object], binary_encoder: 'BinaryEncoding') -> list[object]:
    decoded_items: list[object] = []
    append = decoded_items.append

    for item in items:
        if isinstance(item, dict):
            append(_decode_dict(item, binary_encoder))
        elif isinstance(item, list):
            append(_decode_list(item, binary_encoder))
        else:
            append(item)

    return decoded_items


def _decode_dict(items: dict[object, object], binary_encoder: 'BinaryEncoding') -> dict[str, object]:
    decode_map = binary_encoder.decode_map
    root: dict[str, object] = {}
    stack: list[tuple[object, dict[str, object]]] = [(iter(items.items()), root)]

    while stack:
        iterator, target = stack[-1]
        try:
            key, value = next(iterator)
        except StopIteration:
            stack.pop()
            continue

        if isinstance(key, str):
            decoded_key = key
        else:
            decoded_key = decode_map.get(key)
            if decoded_key is None:
                raise BinaryEncodingMissing(key)

        if isinstance(value, dict):
            child: dict[str, object] = {}
            target[decoded_key] = child
            stack.append((iter(value.items()), child))
        elif isinstance(value, list):
            target[decoded_key] = _decode_list(value, binary_encoder)
        else:
            target[decoded_key] = value

    return root


def decode_keys(given: object, binary_encoder: 'BinaryEncoding') -> object:
    if isinstance(given, dict):
        return _decode_dict(given, binary_encoder)
    if isinstance(given, list):
        return _decode_list(given, binary_encoder)
    return given
