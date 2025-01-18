from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
    from uapi.internal.types.UType import UType


class ParseContext:
    document_name: str
    uapi_schema_document_names_to_pseudo_json: dict[str, list[object]]
    uapi_schema_document_names_to_json: dict[str, str]
    schema_keys_to_document_name: dict[str, str]
    schema_keys_to_index: dict[str, int]
    parsed_types: dict[str, 'UType']
    all_parse_failures: list['SchemaParseFailure']
    failed_types: set[str]

    def __init__(self, document_name: str, uapi_schema_document_names_to_pseudo_json: dict[str, list[object]],
                 uapi_schema_document_names_to_json: dict[str, str],
                 schema_keys_to_document_name: dict[str, str], schema_keys_to_index: dict[str, int],
                 parsed_types: dict[str, 'UType'], all_parse_failures: list['SchemaParseFailure'], failed_types: set[str]) -> None:
        self.document_name = document_name
        self.uapi_schema_document_names_to_pseudo_json = uapi_schema_document_names_to_pseudo_json
        self.uapi_schema_document_names_to_json = uapi_schema_document_names_to_json
        self.schema_keys_to_document_name = schema_keys_to_document_name
        self.schema_keys_to_index = schema_keys_to_index
        self.parsed_types = parsed_types
        self.all_parse_failures = all_parse_failures
        self.failed_types = failed_types

    def copy(self, document_name: Optional[str] = None) -> 'ParseContext':
        return ParseContext(document_name if document_name is not None else self.document_name,
                            self.uapi_schema_document_names_to_pseudo_json, self.uapi_schema_document_names_to_json,
                            self.schema_keys_to_document_name, self.schema_keys_to_index,
                            self.parsed_types, self.all_parse_failures, self.failed_types)
