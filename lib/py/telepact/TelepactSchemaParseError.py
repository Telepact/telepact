from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .internal.schema.SchemaParseFailure import SchemaParseFailure


class TelepactSchemaParseError(Exception):
    """
    Indicates failure to parse a telepact Schema.
    """

    def __init__(self, schema_parse_failures: list['SchemaParseFailure'], telepact_schema_document_names_to_json: dict[str, str]):
        from .internal.schema.MapSchemaParseFailuresToPseudoJson import map_schema_parse_failures_to_pseudo_json
        super().__init__(str(map_schema_parse_failures_to_pseudo_json(
            schema_parse_failures, telepact_schema_document_names_to_json)))
        self.schema_parse_failures = schema_parse_failures
        self.schema_parse_failures_pseudo_json = map_schema_parse_failures_to_pseudo_json(
            schema_parse_failures, telepact_schema_document_names_to_json)
