from typing import TYPE_CHECKING
import re

if TYPE_CHECKING:
    from uapi.UApiSchema import UApiSchema


def create_uapi_schema_from_file_json_map(json_documents: dict[str, str]) -> 'UApiSchema':
    from uapi.internal.schema.NewUApiSchema import new_uapi_schema
    from uapi.internal.schema.GetInternalUApiJson import get_internal_uapi_json
    from uapi.internal.schema.GetAuthUApiJson import get_auth_uapi_json

    final_json_documents = json_documents.copy()
    final_json_documents["internal_"] = get_internal_uapi_json()

    # Determine if we need to add the auth schema
    for json in json_documents.values():
        regex = re.compile(r'"struct\.Auth_"\s*:')
        matcher = regex.search(json)
        if matcher:
            final_json_documents["auth_"] = get_auth_uapi_json()
            break

    return new_uapi_schema(final_json_documents)
