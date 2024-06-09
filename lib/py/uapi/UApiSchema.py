from typing import list, dict, object, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
    from uapi.internal.types.UType import UType


class UApiSchema:
    """
    A parsed uAPI schema.
    """

    def __init__(self, original: list[object], parsed: dict[str, 'UType'], parsed_request_headers: dict[str, 'UFieldDeclaration'],
                 parsed_response_headers: dict[str, 'UFieldDeclaration'], type_extensions: dict[str, 'UType']):
        self.original = original
        self.parsed = parsed
        self.parsed_request_headers = parsed_request_headers
        self.parsed_response_headers = parsed_response_headers
        self.type_extensions = type_extensions

    @staticmethod
    def from_json(json: str) -> 'UApiSchema':
        from uapi.internal.schema.NewUApiSchema import new_uapi_schema
        return new_uapi_schema(json, {})

    @staticmethod
    def extend(base: 'UApiSchema', json: str) -> 'UApiSchema':
        from uapi.internal.schema.ExtendUApiSchema import extend_uapi_schema
        return extend_uapi_schema(base, json, {})
