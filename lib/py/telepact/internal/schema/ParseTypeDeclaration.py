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

import re
from typing import TYPE_CHECKING

from ...internal.schema.SchemaParseFailure import SchemaParseFailure
from ..types.TTypeDeclaration import TTypeDeclaration

if TYPE_CHECKING:
    from ..types.TType import TType
    from ...internal.schema.ParseContext import ParseContext

def parse_type_declaration(
    path: list[object],
    type_declaration_object: object,
    ctx: 'ParseContext'
) -> 'TTypeDeclaration':
    from ...internal.types.TArray import TArray
    from ...internal.types.TObject import TObject
    from ...TelepactSchemaParseError import TelepactSchemaParseError
    from ...internal.schema.GetOrParseType import get_or_parse_type
    from ...internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure

    if isinstance(type_declaration_object, str):
        root_type_string = type_declaration_object

        regex_string = r"^(.*?)(\?)?$"
        regex = re.compile(regex_string)

        matcher = regex.match(root_type_string)
        if not matcher:
            raise TelepactSchemaParseError(
                [SchemaParseFailure(ctx.document_name, path,
                                    "StringRegexMatchFailed", {"regex": regex_string})],
                ctx.telepact_schema_document_names_to_json
            )

        type_name = matcher.group(1)
        nullable = matcher.group(2) is not None

        t_type = get_or_parse_type(path, type_name, ctx)

        if t_type.get_type_parameter_count() != 0:
            raise TelepactSchemaParseError(
                [SchemaParseFailure(ctx.document_name, path,
                                    "ArrayLengthUnexpected",
                                    {"actual": 1, "expected": t_type.get_type_parameter_count() + 1})],
                ctx.telepact_schema_document_names_to_json
            )

        return TTypeDeclaration(t_type, nullable, [])

    elif isinstance(type_declaration_object, list):
        list_object = type_declaration_object

        if len(list_object) != 1:
            raise TelepactSchemaParseError(
                [SchemaParseFailure(ctx.document_name, path,
                                    "ArrayLengthUnexpected", {"actual": len(list_object), "expected": 1})],
                ctx.telepact_schema_document_names_to_json
            )

        element_type_declaration = list_object[0]
        new_path = path + [0]

        array_type = TArray()
        parsed_element_type = parse_type_declaration(new_path, element_type_declaration, ctx)

        return TTypeDeclaration(array_type, False, [parsed_element_type])

    elif isinstance(type_declaration_object, dict):
        map_object = type_declaration_object

        if len(map_object) != 1:
            raise TelepactSchemaParseError(
                [SchemaParseFailure(ctx.document_name, path,
                                    "ObjectSizeUnexpected", {"actual": len(map_object), "expected": 1})],
                ctx.telepact_schema_document_names_to_json
            )

        key, value = next(iter(map_object.items()))

        if not isinstance(key, str) or key != "string":
            key_path = path + [key]
            raise TelepactSchemaParseError(
                [
                    SchemaParseFailure(ctx.document_name, path, "RequiredObjectKeyMissing", {"key": "string"}),
                    SchemaParseFailure(ctx.document_name, key_path, "ObjectKeyDisallowed", {}),
                ],
                ctx.telepact_schema_document_names_to_json
            )

        new_path = path + [key]

        object_type = TObject()
        parsed_value_type = parse_type_declaration(new_path, value, ctx)

        return TTypeDeclaration(object_type, False, [parsed_value_type])

    else:
        failures = get_type_unexpected_parse_failure(
            ctx.document_name, path, type_declaration_object, "StringOrArrayOrObject"
        )
        raise TelepactSchemaParseError(failures, ctx.telepact_schema_document_names_to_json)
