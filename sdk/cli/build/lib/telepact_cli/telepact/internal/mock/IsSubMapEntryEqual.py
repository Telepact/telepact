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

def is_sub_map_entry_equal(part_value: object, whole_value: object) -> bool:
    from ...internal.mock.IsSubMap import is_sub_map
    from ...internal.mock.PartiallyMatches import partially_matches

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
