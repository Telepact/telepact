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

import base64
from typing import TYPE_CHECKING, cast

from ..RandomGenerator import RandomGenerator
from .generation.GenerateContext import GenerateContext

if TYPE_CHECKING:
    from ..TelepactSchema import TelepactSchema
    from .types.TFieldDeclaration import TFieldDeclaration
    from .types.TType import TType


_EXAMPLE_COLLECTION_LENGTH = 2


def get_api_definitions_with_examples(
    telepact_schema: 'TelepactSchema',
    include_internal: bool,
) -> list[object]:
    definitions = telepact_schema.full if include_internal else telepact_schema.original
    default_fn_scope = _get_default_fn_scope(telepact_schema.parsed)

    return [
        _add_examples_to_definition(
            cast(dict[str, object], definition),
            telepact_schema,
            default_fn_scope,
        )
        for definition in definitions
    ]


def get_api_definition_examples(
    telepact_schema: 'TelepactSchema',
    schema_key: str,
    include_internal: bool,
) -> dict[str, object] | None:
    definitions = telepact_schema.full if include_internal else telepact_schema.original
    definition = next((
        cast(dict[str, object], candidate)
        for candidate in definitions
        if _get_schema_key(cast(dict[str, object], candidate)) == schema_key
    ), None)
    if definition is None:
        return None

    definition_with_examples = _add_examples_to_definition(
        definition,
        telepact_schema,
        _get_default_fn_scope(telepact_schema.parsed),
    )
    return {
        key: value
        for key, value in definition_with_examples.items()
        if key in {'example', 'inputExample', 'outputExample'}
    }


def _add_examples_to_definition(
    definition: dict[str, object],
    telepact_schema: 'TelepactSchema',
    default_fn_scope: str,
) -> dict[str, object]:
    schema_key = _get_schema_key(definition)
    cloned_definition = dict(definition)

    if schema_key.startswith('info.'):
        cloned_definition['example'] = {}
        return cloned_definition

    random_generator = RandomGenerator(_EXAMPLE_COLLECTION_LENGTH, _EXAMPLE_COLLECTION_LENGTH)

    if schema_key.startswith('fn.'):
        ctx = GenerateContext(True, False, True, schema_key, random_generator)
        cloned_definition['inputExample'] = _normalize_example_value(
            telepact_schema.parsed[schema_key].generate_random_value(
                None, False, [], ctx)
        )
        cloned_definition['outputExample'] = _normalize_example_value(
            telepact_schema.parsed[
                schema_key + '.->'
            ].generate_random_value(None, False, [], ctx)
        )
        return cloned_definition

    if schema_key.startswith('headers.'):
        ctx = GenerateContext(True, False, True, default_fn_scope, random_generator)
        cloned_definition['inputExample'] = _generate_header_example(
            cast(dict[str, object], definition.get(schema_key, {})),
            telepact_schema.parsed_request_headers,
            ctx,
        )
        cloned_definition['outputExample'] = _generate_header_example(
            cast(dict[str, object], definition.get('->', {})),
            telepact_schema.parsed_response_headers,
            ctx,
        )
        return cloned_definition

    if schema_key.startswith('errors.'):
        ctx = GenerateContext(True, False, True, default_fn_scope, random_generator)
        cloned_definition['example'] = _generate_raw_union_example(
            cast(list[object], definition[schema_key]),
            telepact_schema,
            ctx,
        )
        return cloned_definition

    ctx = GenerateContext(True, False, True, default_fn_scope, random_generator)
    cloned_definition['example'] = _normalize_example_value(
        telepact_schema.parsed[schema_key].generate_random_value(
            None, False, [], ctx)
    )
    return cloned_definition


def _generate_header_example(
    header_definition: dict[str, object],
    parsed_headers: dict[str, 'TFieldDeclaration'],
    ctx: GenerateContext,
) -> dict[str, object]:
    example: dict[str, object] = {}

    for header_name in sorted(header_definition.keys()):
        example[header_name] = _normalize_example_value(
            parsed_headers[header_name].type_declaration.generate_random_value(
                None, False, ctx)
        )

    return example


def _generate_raw_union_example(
    union_definition: list[object],
    telepact_schema: 'TelepactSchema',
    ctx: GenerateContext,
) -> dict[str, object]:
    tags = sorted([
        cast(tuple[str, dict[str, object]], next(
            (key, cast(dict[str, object], value))
            for key, value in cast(dict[str, object], tag_definition).items()
            if key != '///'
        ))
        for tag_definition in union_definition
    ], key=lambda entry: entry[0])
    tag_name, tag_payload = tags[ctx.random_generator.next_int_with_ceiling(len(tags))]
    return {
        tag_name: _generate_raw_struct_example(tag_payload, telepact_schema, ctx),
    }


def _generate_raw_struct_example(
    struct_definition: dict[str, object],
    telepact_schema: 'TelepactSchema',
    ctx: GenerateContext,
) -> dict[str, object]:
    example: dict[str, object] = {}

    for field_name in sorted(struct_definition.keys()):
        optional = field_name.endswith('!')
        if optional:
            if not ctx.include_optional_fields or (
                ctx.randomize_optional_fields and ctx.random_generator.next_boolean()
            ):
                continue
        elif not ctx.always_include_required_fields and ctx.random_generator.next_boolean():
            continue

        example[field_name] = _generate_raw_type_example(
            struct_definition[field_name],
            telepact_schema,
            ctx,
        )

    return example


def _generate_raw_type_example(
    type_expression: object,
    telepact_schema: 'TelepactSchema',
    ctx: GenerateContext,
) -> object:
    if isinstance(type_expression, str):
        nullable = type_expression.endswith('?')
        non_nullable_type_expression = type_expression[:-1] if nullable else type_expression
        if nullable and ctx.random_generator.next_boolean():
            return None

        if non_nullable_type_expression == 'boolean':
            return ctx.random_generator.next_boolean()
        if non_nullable_type_expression == 'integer':
            return ctx.random_generator.next_int()
        if non_nullable_type_expression == 'number':
            return ctx.random_generator.next_double()
        if non_nullable_type_expression == 'string':
            return ctx.random_generator.next_string()
        if non_nullable_type_expression == 'any':
            select_type = ctx.random_generator.next_int_with_ceiling(3)
            if select_type == 0:
                return ctx.random_generator.next_boolean()
            if select_type == 1:
                return ctx.random_generator.next_int()
            return ctx.random_generator.next_string()
        if non_nullable_type_expression == 'bytes':
            return base64.b64encode(ctx.random_generator.next_bytes()).decode()

        return _normalize_example_value(
            telepact_schema.parsed[non_nullable_type_expression].generate_random_value(
                None, False, [], ctx)
        )

    if isinstance(type_expression, list):
        return [
            _generate_raw_type_example(type_expression[0], telepact_schema, ctx)
            for _ in range(ctx.random_generator.next_collection_length())
        ]

    if isinstance(type_expression, dict):
        if set(type_expression.keys()) == {'string'}:
            return {
                ctx.random_generator.next_string(): _generate_raw_type_example(
                    type_expression['string'], telepact_schema, ctx)
                for _ in range(ctx.random_generator.next_collection_length())
            }

    return None


def _normalize_example_value(value: object) -> object:
    if isinstance(value, bytes):
        return base64.b64encode(value).decode()

    if isinstance(value, list):
        return [_normalize_example_value(entry) for entry in value]

    if isinstance(value, dict):
        return {
            key: _normalize_example_value(entry)
            for key, entry in value.items()
        }

    return value


def _get_default_fn_scope(parsed_types: dict[str, 'TType']) -> str:
    non_internal_functions = sorted([
        schema_key for schema_key in parsed_types.keys()
        if schema_key.startswith('fn.') and not schema_key.endswith('.->') and not schema_key.endswith('_')
    ])
    if non_internal_functions:
        return non_internal_functions[0]

    all_functions = sorted([
        schema_key for schema_key in parsed_types.keys()
        if schema_key.startswith('fn.') and not schema_key.endswith('.->')
    ])
    if all_functions:
        return all_functions[0]

    return 'fn.ping_'


def _get_schema_key(definition: dict[str, object]) -> str:
    for key in definition.keys():
        if key not in {'///', '->', '_errors'}:
            return key

    raise ValueError(f'Schema entry has no schema key: {definition}')
