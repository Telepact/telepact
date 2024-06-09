from typing import List, Dict
from collections import OrderedDict


def find_schema_key(definition: Dict[str, object], index: int) -> str:
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
    import re

    regex = "^(errors|((fn|requestHeader|responseHeader|info)|((struct|union|_ext)(<[0-2]>)?))\\..*)"
    matches = []

    keys = sorted(list(definition.keys()))

    for e in keys:
        if re.match(regex, e):
            matches.append(e)

    if len(matches) == 1:
        return matches[0]
    else:
        parse_failure = SchemaParseFailure([index],
                                           "ObjectKeyRegexMatchCountUnexpected",
                                           {"regex": regex, "actual": len(
                                               matches), "expected": 1, "keys": keys},
                                           None)
        raise UApiSchemaParseError([parse_failure])
