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

from typing import Callable, TYPE_CHECKING, cast, Awaitable

from ..Message import Message
from .types.TTypeDeclaration import TTypeDeclaration

if TYPE_CHECKING:
    from .types.TUnion import TUnion
    from ..internal.validation.ValidationFailure import ValidationFailure
    from .types.TType import TType
    from ..TelepactSchema import TelepactSchema


async def handle_message(
    request_message: 'Message',
    telepact_schema: 'TelepactSchema',
    handler: Callable[['Message'], Awaitable['Message']],
    on_error: Callable[[Exception], None],
) -> 'Message':
    from ..internal.SelectStructFields import select_struct_fields
    from ..internal.validation.GetInvalidErrorMessage import get_invalid_error_message
    from ..internal.validation.ValidateHeaders import validate_headers
    from ..internal.validation.ValidateResult import validate_result
    from .types.TFn import TFn
    from ..internal.validation.ValidateContext import ValidateContext

    print("Handling message")

    response_headers: dict[str, object] = {}
    request_headers: dict[str, object] = request_message.headers
    request_body: dict[str, object] = request_message.body
    parsed_telepact_schema: dict[str, TType] = telepact_schema.parsed
    request_entry: tuple[str, object] = next(iter(request_body.items()))

    request_target_init = request_entry[0]
    request_payload = cast(
        dict[str, object], request_entry[1])

    unknown_target: str | None
    request_target: str
    if request_target_init not in parsed_telepact_schema:
        unknown_target = request_target_init
        request_target = "fn.ping_"
    else:
        unknown_target = None
        request_target = request_target_init

    function_type = cast(TFn, parsed_telepact_schema[request_target])
    result_union_type: TUnion = function_type.result

    call_id = request_headers.get("@id_")
    if call_id is not None:
        response_headers["@id_"] = call_id

    if "_parseFailures" in request_headers:
        parse_failures = cast(list[object], request_headers["_parseFailures"])
        new_error_result: dict[str, object] = {
            "ErrorParseFailure_": {"reasons": parse_failures}
        }

        validate_result(result_union_type, new_error_result)

        return Message(response_headers, new_error_result)

    request_header_validation_failures: list[ValidationFailure] = validate_headers(
        request_headers, telepact_schema.parsed_request_headers, function_type
    )
    if request_header_validation_failures:
        return get_invalid_error_message(
            "ErrorInvalidRequestHeaders_",
            request_header_validation_failures,
            result_union_type,
            response_headers,
        )

    if "@bin_" in request_headers:
        client_known_binary_checksums = cast(
            list[object], request_headers["@bin_"])

        response_headers["@binary_"] = True
        response_headers["@clientKnownBinaryChecksums_"] = client_known_binary_checksums

        if "@pac_" in request_headers:
            response_headers["@pac_"] = request_headers["@pac_"]

    select_struct_fields_header: dict[str, object] | None = cast(dict[str, object] | None, request_headers.get(
        "@select_"
    ))

    if unknown_target is not None:
        new_error_result = {
            "ErrorInvalidRequestBody_": {
                "cases": [
                    {
                        "path": [unknown_target],
                        "reason": {"FunctionUnknown": {}},
                    }
                ]
            }
        }

        validate_result(result_union_type, new_error_result)
        return Message(response_headers, new_error_result)

    function_type_call: TUnion = function_type.call

    call_validation_failures: list[ValidationFailure] = function_type_call.validate(
        request_body, [], ValidateContext(None, None, use_bytes=False)
    )
    if call_validation_failures:
        return get_invalid_error_message(
            "ErrorInvalidRequestBody_",
            call_validation_failures,
            result_union_type,
            response_headers,
        )

    unsafe_response_enabled = cast(bool, request_headers.get("@unsafe_", False))

    call_message: Message = Message(
        request_headers, {request_target: request_payload})

    result_message: Message
    if request_target == "fn.ping_":
        result_message = Message({}, {"Ok_": {}})
    elif request_target == "fn.api_":
        result_message = Message({}, {"Ok_": {"api": telepact_schema.original}})
    else:
        try:
            result_message = await handler(call_message)
        except Exception as e:
            try:
                on_error(e)
            except Exception:
                pass
            return Message(response_headers, {"ErrorUnknown_": {}})

    result_union: dict[str, object] = result_message.body

    result_message.headers.update(response_headers)
    final_response_headers: dict[str, object] = result_message.headers

    skip_result_validation: bool = unsafe_response_enabled
    if not skip_result_validation:
        use_binary = cast(bool, response_headers.get("@binary_", False))
        ctx = ValidateContext(select_struct_fields_header, function_type.name, use_bytes=use_binary)
        result_validation_failures: list[ValidationFailure] = result_union_type.validate(
            result_union, [], ctx)
        if result_validation_failures:
            res = get_invalid_error_message(
                "ErrorInvalidResponseBody_",
                result_validation_failures,
                result_union_type,
                response_headers,
            )
            on_error(Exception(
                f"Response validation failed: {result_validation_failures}. Actual response: {result_union}"))
            return res
        response_header_validation_failures: list[ValidationFailure] = validate_headers(
            final_response_headers, telepact_schema.parsed_response_headers, function_type
        )
        if response_header_validation_failures:
            return get_invalid_error_message(
                "ErrorInvalidResponseHeaders_",
                response_header_validation_failures,
                result_union_type,
                response_headers,
            )
        if ctx.coercions:
            response_headers["@base64_"] = ctx.coercions

    final_result_union: dict[str, object]
    if select_struct_fields_header is not None:
        final_result_union = cast(dict[str, object], select_struct_fields(
            TTypeDeclaration(result_union_type, False, []),
            result_union,
            select_struct_fields_header,
        ))
    else:
        final_result_union = result_union

    return Message(final_response_headers, final_result_union)
