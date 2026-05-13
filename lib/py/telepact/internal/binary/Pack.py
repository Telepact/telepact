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

def pack(value: object) -> object:
    value_type = type(value)
    if value_type is list:
        from .PackList import pack_list
        return pack_list(value)
    if value_type is dict:
        new_map = {}

        for key, val in value.items():
            new_map[key] = pack(val)

        return new_map
    return value
