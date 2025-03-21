#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from typing import TYPE_CHECKING
import re

if TYPE_CHECKING:
    from ...TelepactSchema import TelepactSchema


def create_vers_api_schema_from_file_json_map(json_documents: dict[str, str]) -> 'TelepactSchema':
    from .ParseTelepactSchema import parse_vers_api_schema
    from .GetInternalTelepactJson import get_internal_vers_api_json
    from .GetAuthTelepactJson import get_auth_vers_api_json

    final_json_documents = json_documents.copy()
    final_json_documents["internal_"] = get_internal_vers_api_json()

    # Determine if we need to add the auth schema
    for json in json_documents.values():
        regex = re.compile(r'"struct\.Auth_"\s*:')
        matcher = regex.search(json)
        if matcher:
            final_json_documents["auth_"] = get_auth_vers_api_json()
            break

    return parse_vers_api_schema(final_json_documents)
