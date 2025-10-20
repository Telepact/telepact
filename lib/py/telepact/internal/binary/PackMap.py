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

from ...internal.binary.BinaryPackNode import BinaryPackNode
from ...internal.binary.Pack import UNDEFINED_BYTE, pack_map as _pack_map


def pack_map(m: dict[object, object], header: list[object], key_index_map: dict[int, 'BinaryPackNode']) -> list[object]:
    return _pack_map(m, header, key_index_map)
