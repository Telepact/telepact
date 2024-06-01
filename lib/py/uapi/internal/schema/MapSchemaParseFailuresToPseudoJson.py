from typing import List, Dict, TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure


def map_schema_parse_failures_to_pseudo_json(schema_parse_failures: List['SchemaParseFailure']) -> List[Dict[str, object]]:
    pseudo_json_list = []
    for f in schema_parse_failures:
        pseudo_json = defaultdict(dict)
        pseudo_json["path"] = f.path
        pseudo_json["reason"] = {f.reason: f.data}
        if f.key is not None:
            pseudo_json["key!"] = f.key
        pseudo_json_list.append(dict(pseudo_json))
    return pseudo_json_list
