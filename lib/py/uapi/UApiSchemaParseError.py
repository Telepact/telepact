from typing import list, object, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure


class UApiSchemaParseError(Exception):
    """
    Indicates failure to parse a uAPI Schema.
    """

    def __init__(self, schema_parse_failures: list['SchemaParseFailure'], cause: Exception = None):
        from uapi.internal.schema.MapSchemaParseFailuresToPseudoJson import map_schema_parse_failures_to_pseudo_json
        super().__init__(str(map_schema_parse_failures_to_pseudo_json(schema_parse_failures)))
        self.schema_parse_failures = schema_parse_failures
        self.schema_parse_failures_pseudo_json = map_schema_parse_failures_to_pseudo_json(
            schema_parse_failures)
        self.cause = cause
