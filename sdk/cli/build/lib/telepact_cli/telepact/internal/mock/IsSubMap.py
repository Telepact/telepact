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

from typing import cast


def is_sub_map(part: dict[str, object], whole: dict[str, object]) -> bool:
    from ...internal.mock.IsSubMapEntryEqual import is_sub_map_entry_equal

    for part_key in part.keys():
        whole_value = cast(dict[str, object], whole.get(part_key))
        part_value = cast(dict[str, object], part.get(part_key))
        entry_is_equal = is_sub_map_entry_equal(part_value, whole_value)
        if not entry_is_equal:
            return False
    return True
