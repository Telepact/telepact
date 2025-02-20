from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...internal.schema.SchemaParseFailure import SchemaParseFailure


def map_schema_parse_failures_to_pseudo_json(schema_parse_failures: list['SchemaParseFailure'], uapi_document_name_to_json: dict[str, str]) -> list[dict[str, object]]:
    from ...internal.schema.GetPathDocumentCoordinatesPseudoJson import get_path_document_coordinates_pseudo_json
    pseudo_json_list = []
    for f in schema_parse_failures:
        print(
            f'uapi_document_name_to_json.keys(): {uapi_document_name_to_json.keys()}')
        location = get_path_document_coordinates_pseudo_json(
            f.path, uapi_document_name_to_json[f.document_name])
        pseudo_json: dict[str, object] = {}
        pseudo_json["document"] = f.document_name
        pseudo_json["location"] = location
        pseudo_json["path"] = f.path
        pseudo_json["reason"] = {f.reason: f.data}
        pseudo_json_list.append(dict(pseudo_json))
    return pseudo_json_list
