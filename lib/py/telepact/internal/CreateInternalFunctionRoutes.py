#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
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
