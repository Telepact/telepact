from typing import List, Dict, Any
from uapi.internal.types import UType, UFieldDeclaration
from uapi.internal.schema import extend_u_api_schema, new_u_api_schema


class UApiSchema:
    """
    A parsed uAPI schema.
    """

    def __init__(self, original: List[Any], parsed: Dict[str, UType], parsed_request_headers: Dict[str, UFieldDeclaration],
                 parsed_response_headers: Dict[str, UFieldDeclaration], type_extensions: Dict[str, UType]):
        self.original = original
        self.parsed = parsed
        self.parsed_request_headers = parsed_request_headers
        self.parsed_response_headers = parsed_response_headers
        self.type_extensions = type_extensions

    @staticmethod
    def from_json(json: str) -> 'UApiSchema':
        return new_u_api_schema(json, {})

    @staticmethod
    def extend(base: 'UApiSchema', json: str) -> 'UApiSchema':
        return extend_u_api_schema(base, json, {})
