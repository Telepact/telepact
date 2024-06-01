from typing import List, Dict
from collections import OrderedDict


def find_schema_key(definition: Dict[str, object], index: int) -> str:
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure

    regex = r"^(errors|((fn|request_header|response_header|info)|((struct|union|_ext)(<[0-2]>)?))\..*)"
    matches = []

    keys = sorted(definition.keys())

    for e in keys:
        if e.match(regex):
            matches.append(e)

    if len(matches) == 1:
        return matches[0]
    else:
        parse_failure = SchemaParseFailure([index],
                                           "ObjectKeyRegexMatchCountUnexpected",
                                           OrderedDict(
                                               regex=regex,
                                               actual=len(matches),
                                               expected=1,
                                               keys=keys
        ),
            None)
        raise UApiSchemaParseError([parse_failure])
