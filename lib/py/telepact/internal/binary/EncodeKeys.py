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
    from ...internal.binary.BinaryEncoding import BinaryEncoding


def encode_keys(given: object, binary_encoding: 'BinaryEncoding') -> object:
    if given is None:
        return given

    encode_map = binary_encoding.encode_map

    if isinstance(given, dict):
        root: dict[object, object] = {}
        stack: list[tuple[object, object, bool]] = [(iter(given.items()), root, True)]
    elif isinstance(given, list):
        root = [None] * len(given)
        stack = [(iter(enumerate(given)), root, False)]
    else:
        return given

    while stack:
        iterator, target, is_mapping = stack[-1]
        try:
            key, value = next(iterator)
        except StopIteration:
            stack.pop()
            continue

        final_key = encode_map.get(key, key) if is_mapping else key

        if isinstance(value, dict):
            child: dict[object, object] = {}
            target[final_key] = child
            stack.append((iter(value.items()), child, True))
        elif isinstance(value, list):
            child = [None] * len(value)
            target[final_key] = child
            stack.append((iter(enumerate(value)), child, False))
        else:
            target[final_key] = value

    return root
