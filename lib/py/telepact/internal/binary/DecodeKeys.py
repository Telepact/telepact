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


def _decode_dict(items: dict[object, object], binary_encoder: 'BinaryEncoding') -> dict[str, object]:
    decode_map = binary_encoder.decode_map
    root: dict[str, object] = {}
    stack: list[tuple[object, object, bool]] = [(iter(items.items()), root, True)]

    while stack:
        iterator, target, is_mapping = stack[-1]
        try:
            key, value = next(iterator)
        except StopIteration:
            stack.pop()
            continue

        if is_mapping:
            if isinstance(key, str):
                decoded_key = key
            else:
                decoded_key = decode_map.get(key)
                if decoded_key is None:
                    raise BinaryEncodingMissing(key)
        else:
            decoded_key = key

        if isinstance(value, dict):
            child: dict[str, object] = {}
            target[decoded_key] = child
            stack.append((iter(value.items()), child, True))
        elif isinstance(value, list):
            child = [None] * len(value)
            target[decoded_key] = child
            stack.append((iter(enumerate(value)), child, False))
        else:
            target[decoded_key] = value

    return root


def decode_keys(given: object, binary_encoder: 'BinaryEncoding') -> object:
    if isinstance(given, dict):
        return _decode_dict(given, binary_encoder)
    if isinstance(given, list):
        root = [None] * len(given)
        decode_map = binary_encoder.decode_map
        stack: list[tuple[object, object, bool]] = [(iter(enumerate(given)), root, False)]

        while stack:
            iterator, target, is_mapping = stack[-1]
            try:
                key, value = next(iterator)
            except StopIteration:
                stack.pop()
                continue

            if is_mapping:
                if isinstance(key, str):
                    decoded_key = key
                else:
                    decoded_key = decode_map.get(key)
                    if decoded_key is None:
                        raise BinaryEncodingMissing(key)
            else:
                decoded_key = key

            if isinstance(value, dict):
                child: dict[str, object] = {}
                target[decoded_key] = child
                stack.append((iter(value.items()), child, True))
            elif isinstance(value, list):
                child = [None] * len(value)
                target[decoded_key] = child
                stack.append((iter(enumerate(value)), child, False))
            else:
                target[decoded_key] = value

        return root
    return given
