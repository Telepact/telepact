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
from ..types.TFieldDeclaration import TFieldDeclaration

if TYPE_CHECKING:
    from ..types.TType import TType
    from ...internal.schema.ParseContext import ParseContext


def parse_field(path: list[object], field_declaration: str, type_declaration_value: object,
                is_header: bool,
                ctx: 'ParseContext') -> 'TFieldDeclaration':
    from ...TelepactSchemaParseError import TelepactSchemaParseError
    from ...internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from ...internal.schema.ParseTypeDeclaration import parse_type_declaration

    header_regex_string = r"^@[a-z][a-zA-Z0-9_]*$"
    regex_string = r"^([a-z][a-zA-Z0-9_]*)(!)?$"
    regex_to_use = header_regex_string if is_header else regex_string
    regex = re.compile(regex_to_use)

    matcher = regex.match(field_declaration)
    if not matcher:
        final_path = path + [field_declaration]
        raise TelepactSchemaParseError([SchemaParseFailure(ctx.document_name, final_path,
                                                          "KeyRegexMatchFailed",
                                                          {"regex": regex_to_use})], ctx.telepact_schema_document_names_to_json)

    field_name = matcher.group(0)
    optional = True if is_header else bool(matcher.group(2))

    this_path = path + [field_name]

    type_declaration = parse_type_declaration(this_path,
                                              type_declaration_value, ctx)

    return TFieldDeclaration(field_name, type_declaration, optional)
