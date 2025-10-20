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

def generate_random_value_of_type(
        blueprint_value: object, use_blueprint_value: bool,
        this_type: object, nullable: bool,
        type_parameters: list[object], ctx: object) -> object:
    random_generator = getattr(ctx, "random_generator", None)
    next_boolean = getattr(random_generator, "next_boolean", None)

    should_return_none = (
        nullable
        and not use_blueprint_value
        and callable(next_boolean)
        and bool(next_boolean())
    )

    if should_return_none:
        return None

    generate = getattr(this_type, "generate_random_value", None)
    if callable(generate):
        return generate(blueprint_value, use_blueprint_value, type_parameters, ctx)

    return blueprint_value
