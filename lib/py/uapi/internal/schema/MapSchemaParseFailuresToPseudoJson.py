from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure


def map_schema_parse_failures_to_pseudo_json(schema_parse_failures: list['SchemaParseFailure']) -> list[dict[str, object]]:
    pseudo_json_list = []
    for f in schema_parse_failures:
        pseudo_json: dict[str, object] = {}
        pseudo_json["document"] = f.document_name
        pseudo_json["path"] = f.path
        pseudo_json["reason"] = {f.reason: f.data}
        pseudo_json_list.append(dict(pseudo_json))
    return pseudo_json_list
