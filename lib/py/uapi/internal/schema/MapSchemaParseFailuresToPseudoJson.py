from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure


def map_schema_parse_failures_to_pseudo_json(schema_parse_failures: list['SchemaParseFailure'], uapi_document_name: dict[str, str]) -> list[dict[str, object]]:
    from uapi.internal.schema.GetPathDocumentCoordinatesPseudoJson import get_path_document_coordinates_pseudo_json
    pseudo_json_list = []
    for f in schema_parse_failures:
        # location = None if f.document_name not in uapi_document_name else get_path_document_coordinates_pseudo_json(
        #    f.path, uapi_document_name[f.document_name])
        location = None
        pseudo_json: dict[str, object] = {}
        pseudo_json["document"] = f.document_name
        if location is not None and False:  # TODO: remove 'and False'
            pseudo_json["location"] = location
        else:
            pseudo_json["path"] = f.path
        pseudo_json["reason"] = {f.reason: f.data}
        pseudo_json_list.append(dict(pseudo_json))
    return pseudo_json_list
