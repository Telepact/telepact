from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
    from uapi.internal.types.UType import UType


class ParseContext:
    document_name: str
    path: list[object]
    uapi_schema_document_names_to_pseudo_json: dict[str, list[object]]
    schema_keys_to_document_name: dict[str, str]
    schema_keys_to_index: dict[str, int]
    parsed_types: dict[str, 'UType']
    all_parse_failures: list['SchemaParseFailure']
    failed_types: set[str]

    def __init__(self, document_name: str, path: list[object], uapi_schema_document_names_to_pseudo_json: dict[str, list[object]],
                 schema_keys_to_document_name: dict[str, str], schema_keys_to_index: dict[str, int],
                 parsed_types: dict[str, 'UType'], all_parse_failures: list['SchemaParseFailure'], failed_types: set[str]) -> None:
        self.document_name = document_name
        self.path = path
        self.uapi_schema_document_names_to_pseudo_json = uapi_schema_document_names_to_pseudo_json
        self.schema_keys_to_document_name = schema_keys_to_document_name
        self.schema_keys_to_index = schema_keys_to_index
        self.parsed_types = parsed_types
        self.all_parse_failures = all_parse_failures
        self.failed_types = failed_types

    def copy(self, document_name: Optional[str] = None, path: Optional[list[object]] = None, uapi_schema_document_names_to_pseudo_json: Optional[dict[str, list[object]]] = None,
             schema_keys_to_document_name: Optional[dict[str, str]] = None, schema_keys_to_index: Optional[dict[str, int]] = None,
             parsed_types: Optional[dict[str, 'UType']] = None, all_parse_failures: Optional[list['SchemaParseFailure']] = None, failed_types: Optional[set[str]] = None) -> 'ParseContext':
        return ParseContext(document_name if document_name is not None else self.document_name,
                            path if path is not None else self.path,
                            uapi_schema_document_names_to_pseudo_json if uapi_schema_document_names_to_pseudo_json is not None else self.uapi_schema_document_names_to_pseudo_json,
                            schema_keys_to_document_name if schema_keys_to_document_name is not None else self.schema_keys_to_document_name,
                            schema_keys_to_index if schema_keys_to_index is not None else self.schema_keys_to_index,
                            parsed_types if parsed_types is not None else self.parsed_types,
                            all_parse_failures if all_parse_failures is not None else self.all_parse_failures,
                            failed_types if failed_types is not None else self.failed_types)

    def with_path(self, path: list[object]) -> 'ParseContext':
        return ParseContext(self.document_name, path, self.uapi_schema_document_names_to_pseudo_json,
                            self.schema_keys_to_document_name, self.schema_keys_to_index,
                            self.parsed_types, self.all_parse_failures, self.failed_types)
