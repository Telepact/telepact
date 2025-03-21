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

from collections import OrderedDict


def find_schema_key(document_name: str, definition: dict[str, object], index: int, document_names_to_json: dict[str, str]) -> str:
    from ...TelepactSchemaParseError import TelepactSchemaParseError
    from ...internal.schema.SchemaParseFailure import SchemaParseFailure
    import re

    regex = "^(((fn|errors|headers|info)|((struct|union|_ext)(<[0-2]>)?))\\..*)"
    matches = []

    keys = sorted(list(definition.keys()))

    for e in keys:
        if re.match(regex, e):
            matches.append(e)

    if len(matches) == 1:
        return matches[0]
    else:
        parse_failure = SchemaParseFailure(document_name, [index],
                                           "ObjectKeyRegexMatchCountUnexpected",
                                           {"regex": regex, "actual": len(
                                               matches), "expected": 1, "keys": keys})
        raise TelepactSchemaParseError([parse_failure], document_names_to_json)
