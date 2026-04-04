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

from ...TelepactSchemaParseError import TelepactSchemaParseError
from ...internal.schema.SchemaParseFailure import SchemaParseFailure
from ..types.TArray import TArray
from ..types.TFieldDeclaration import TFieldDeclaration
from ..types.TObject import TObject
from ..types.TStruct import TStruct
from ..types.TType import TType
from ..types.TTypeDeclaration import TTypeDeclaration
from ..types.TUnion import TUnion


def _type_declaration_terminates(type_declaration: TTypeDeclaration, terminating_type_names: set[str]) -> bool:
    if type_declaration.nullable:
        return True

    if isinstance(type_declaration.type, (TArray, TObject)):
        return True

    if isinstance(type_declaration.type, (TStruct, TUnion)):
        return type_declaration.type.name in terminating_type_names

    return True


def _struct_fields_terminate(fields: dict[str, TFieldDeclaration], terminating_type_names: set[str]) -> bool:
    return all(
        field.optional or _type_declaration_terminates(field.type_declaration, terminating_type_names)
        for field in fields.values()
    )


def _type_terminates(type_: TType, terminating_type_names: set[str]) -> bool:
    if isinstance(type_, TStruct):
        return _struct_fields_terminate(type_.fields, terminating_type_names)

    if isinstance(type_, TUnion):
        return any(
            _struct_fields_terminate(tag.fields, terminating_type_names)
            for tag in type_.tags.values()
        )

    return True


def validate_type_termination(
    parsed_types: dict[str, TType],
    schema_keys_to_document_name: dict[str, str],
    schema_keys_to_index: dict[str, int],
    telepact_schema_document_names_to_json: dict[str, str],
) -> None:
    terminating_type_names: set[str] = set()

    changed = True
    while changed:
        changed = False
        for type_name, type_ in parsed_types.items():
            if type_name in terminating_type_names:
                continue

            if _type_terminates(type_, terminating_type_names):
                terminating_type_names.add(type_name)
                changed = True

    parse_failures: list[SchemaParseFailure] = []
    for schema_key, document_name in schema_keys_to_document_name.items():
        if schema_key.startswith(('info.', 'headers.', 'errors.')):
            continue

        root_type_names = [schema_key]
        if schema_key.startswith('fn.'):
            root_type_names.append(f'{schema_key}.->')

        for root_type_name in root_type_names:
            if root_type_name in parsed_types and root_type_name not in terminating_type_names:
                path = [schema_keys_to_index[schema_key], '->'] if root_type_name.endswith('.->') else [schema_keys_to_index[schema_key], schema_key]
                parse_failures.append(
                    SchemaParseFailure(
                        document_name,
                        path,
                        'RecursiveTypeUnterminated',
                        {},
                    )
                )

    if parse_failures:
        raise TelepactSchemaParseError(parse_failures, telepact_schema_document_names_to_json)
