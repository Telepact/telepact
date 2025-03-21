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
