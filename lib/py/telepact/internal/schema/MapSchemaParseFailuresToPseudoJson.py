#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...internal.schema.SchemaParseFailure import SchemaParseFailure


def map_schema_parse_failures_to_pseudo_json(schema_parse_failures: list['SchemaParseFailure'], telepact_document_name_to_json: dict[str, str]) -> list[dict[str, object]]:
    from ...internal.schema.DocumentLocators import resolve_document_coordinates
    pseudo_json_list = []
    for f in schema_parse_failures:
        location = resolve_document_coordinates(
            f.path, f.document_name, telepact_document_name_to_json)
        pseudo_json: dict[str, object] = {}
        pseudo_json["document"] = f.document_name
        pseudo_json["location"] = location
        pseudo_json["path"] = f.path
        pseudo_json["reason"] = {f.reason: f.data}
        pseudo_json_list.append(dict(pseudo_json))
    return pseudo_json_list
