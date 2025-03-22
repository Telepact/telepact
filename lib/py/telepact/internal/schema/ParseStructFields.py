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

from typing import TYPE_CHECKING

from ...internal.schema.SchemaParseFailure import SchemaParseFailure

if TYPE_CHECKING:
    from ...internal.schema.ParseContext import ParseContext
    from ..types.TFieldDeclaration import TFieldDeclaration


def parse_struct_fields(path: list[object], reference_struct: dict[str, object], is_header: bool, ctx: 'ParseContext') -> dict[str, 'TFieldDeclaration']:
    from ...TelepactSchemaParseError import TelepactSchemaParseError
    from ...internal.schema.ParseField import parse_field
    from ...internal.schema.GetPathDocumentCoordinatesPseudoJson import get_path_document_coordinates_pseudo_json

    parse_failures = []
    fields: dict[str, 'TFieldDeclaration'] = {}

    for field_declaration, type_declaration_value in reference_struct.items():
        for existing_field in fields.keys():
            existing_field_no_opt = existing_field.split("!")[0]
            field_no_opt = field_declaration.split("!")[0]
            if field_no_opt == existing_field_no_opt:
                final_path = path + [field_declaration]
                final_other_path = path + [existing_field]
                final_other_document_json = ctx.telepact_schema_document_names_to_json[
                    ctx.document_name]
                final_other_location_pseudo_json = get_path_document_coordinates_pseudo_json(
                    final_other_path, final_other_document_json)
                parse_failures.append(SchemaParseFailure(
                    ctx.document_name, final_path, "PathCollision", {
                        "document": ctx.document_name,
                        "path": final_other_path,
                        "location": final_other_location_pseudo_json}))

        try:
            parsed_field = parse_field(path,
                                       field_declaration, type_declaration_value,
                                       is_header, ctx)
            field_name = parsed_field.field_name
            fields[field_name] = parsed_field
        except TelepactSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, ctx.telepact_schema_document_names_to_json)

    return fields
