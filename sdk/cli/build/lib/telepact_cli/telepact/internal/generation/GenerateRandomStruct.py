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

from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from ...RandomGenerator import RandomGenerator
    from ..types.TFieldDeclaration import TFieldDeclaration
    from ..types.TTypeDeclaration import TTypeDeclaration
    from ...internal.generation.GenerateContext import GenerateContext


def generate_random_struct(blueprint_value: object, use_blueprint_value: bool,
                           reference_struct: dict[str, 'TFieldDeclaration'], ctx: 'GenerateContext') -> object:
    sorted_reference_struct = sorted(
        reference_struct.items(), key=lambda x: x[0])

    starting_struct = cast(
        dict[str, object], blueprint_value) if use_blueprint_value else {}

    obj = {}
    for field_name, field_declaration in sorted_reference_struct:
        this_use_blueprint_value = field_name in starting_struct
        type_declaration = field_declaration.type_declaration

        if this_use_blueprint_value:
            this_blueprint_value = starting_struct.get(field_name)
            value = type_declaration.generate_random_value(
                this_blueprint_value, this_use_blueprint_value, ctx)
        else:
            if not field_declaration.optional:
                if not ctx.always_include_required_fields and ctx.random_generator.next_boolean():
                    continue
                value = type_declaration.generate_random_value(
                    None, False, ctx)
            else:
                if not ctx.include_optional_fields or (ctx.randomize_optional_fields and ctx.random_generator.next_boolean()):
                    continue
                value = type_declaration.generate_random_value(
                    None, False, ctx)

        obj[field_name] = value

    return obj
