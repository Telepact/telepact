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

from typing import Dict, List, Union

from ...internal.generation.GenerateContext import GenerateContext


def generate_random_select(possible_selects: dict[str, object], ctx: 'GenerateContext') -> object:
    possible_select = possible_selects[ctx.fn_scope]
    return sub_select(possible_select, ctx)


def sub_select(possible_select_section: object, ctx: 'GenerateContext') -> object:
    if isinstance(possible_select_section, list):
        selected_field_names = []

        for field_name in possible_select_section:
            if ctx.random_generator.next_boolean():
                selected_field_names.append(field_name)

        return sorted(selected_field_names)
    elif isinstance(possible_select_section, dict):
        selected_section: dict[str, object] = {}

        keys = sorted(possible_select_section.keys())

        for key in keys:
            value = possible_select_section[key]
            if ctx.random_generator.next_boolean():
                result = sub_select(value, ctx)
                if isinstance(result, dict) and not result:
                    continue
                selected_section[key] = result

        return selected_section
    else:
        raise ValueError('Invalid possible_select_section')
