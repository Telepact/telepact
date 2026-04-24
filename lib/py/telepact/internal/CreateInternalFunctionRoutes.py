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

from ..FunctionRouter import FunctionRoute
from ..Message import Message
from ..TelepactSchema import TelepactSchema
from .GetApiDefinitionsWithExamples import get_api_definitions_with_examples


def create_internal_function_routes(telepact_schema: TelepactSchema) -> dict[str, FunctionRoute]:
    async def handle_ping(_function_name: str, _request_message: Message) -> Message:
        return Message({}, {"Ok_": {}})

    async def handle_api(_function_name: str, request_message: Message) -> Message:
        request_payload = request_message.get_body_payload()
        include_internal = request_payload.get("includeInternal!") is True
        include_examples = request_payload.get("includeExamples!") is True
        api_definitions = get_api_definitions_with_examples(
            telepact_schema,
            include_internal,
        ) if include_examples else (
            telepact_schema.full if include_internal else telepact_schema.original
        )
        return Message({}, {"Ok_": {"api": api_definitions}})

    return {
        "fn.ping_": handle_ping,
        "fn.api_": handle_api,
    }
