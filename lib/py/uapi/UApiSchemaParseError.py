from typing import List, Any
from uapi.internal.schema import SchemaParseFailure, map_schema_parse_failures_to_pseudo_json


class UApiSchemaParseError(Exception):
    """
    Indicates failure to parse a uAPI Schema.
    """

    def __init__(self, schema_parse_failures: List[SchemaParseFailure], cause: Exception = None):
        super().__init__(str(map_schema_parse_failures_to_pseudo_json(schema_parse_failures)))
        self.schema_parse_failures = schema_parse_failures
        self.schema_parse_failures_pseudo_json = map_schema_parse_failures_to_pseudo_json(
            schema_parse_failures)
        self.cause = cause
