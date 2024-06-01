from typing import List, Dict, Any

from uapi.internal.schema.ExtendUApiSchema import extend_uapi_schema
from uapi.internal.schema.NewUApiSchema import new_uapi_schema
from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
from uapi.internal.types.UType import UType


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
        return new_uapi_schema(json, {})

    @staticmethod
    def extend(base: 'UApiSchema', json: str) -> 'UApiSchema':
        return extend_uapi_schema(base, json, {})
