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
    for part_key in part.keys():
        whole_value = cast(dict[str, object], whole.get(part_key))
        part_value = cast(dict[str, object], part.get(part_key))
        entry_is_equal = is_sub_map_entry_equal(part_value, whole_value)
        if not entry_is_equal:
            return False
    return True


def partially_matches(whole_list: list[object], part_element: object) -> bool:
    for whole_element in whole_list:
        if is_sub_map_entry_equal(part_element, whole_element):
            return True
    return False


def is_sub_map_entry_equal(part_value: object, whole_value: object) -> bool:
    if isinstance(part_value, dict) and isinstance(whole_value, dict):
        return is_sub_map(part_value, whole_value)
    elif isinstance(part_value, list) and isinstance(whole_value, list):
        for part_element in part_value:
            part_matches = partially_matches(whole_value, part_element)
            if not part_matches:
                return False
        return True
    else:
        return part_value == whole_value
