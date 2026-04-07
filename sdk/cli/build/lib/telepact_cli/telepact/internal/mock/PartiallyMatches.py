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

def partially_matches(whole_list: list[object], part_element: object) -> bool:
    from ...internal.mock.IsSubMapEntryEqual import is_sub_map_entry_equal

    for whole_element in whole_list:
        if is_sub_map_entry_equal(part_element, whole_element):
            return True
    return False
