from typing import Callable, TYPE_CHECKING, cast, Awaitable

from ..Message import Message
from .types.VTypeDeclaration import VTypeDeclaration

if TYPE_CHECKING:
    from .types.VUnion import VUnion
    from ..internal.validation.ValidationFailure import ValidationFailure
    from .types.VType import VType
    from ..MsgPactSchema import MsgPactSchema


async def handle_message(
    request_message: 'Message',
    u_api_schema: 'MsgPactSchema',
    handler: Callable[['Message'], Awaitable['Message']],
    on_error: Callable[[Exception], None],
) -> 'Message':
    from ..internal.SelectStructFields import select_struct_fields
    from ..internal.validation.GetInvalidErrorMessage import get_invalid_error_message
    from ..internal.validation.ValidateHeaders import validate_headers
    from ..internal.validation.ValidateResult import validate_result
    from .types.VFn import VFn
    from ..internal.validation.ValidateContext import ValidateContext

    print("Handling message")

    response_headers: dict[str, object] = {}
    request_headers: dict[str, object] = request_message.headers
    request_body: dict[str, object] = request_message.body
    parsed_u_api_schema: dict[str, VType] = u_api_schema.parsed
    request_entry: tuple[str, object] = next(iter(request_body.items()))

    request_target_init = request_entry[0]
    request_payload = cast(
        dict[str, object], request_entry[1])

    unknown_target: str | None
    request_target: str
    if request_target_init not in parsed_u_api_schema:
        unknown_target = request_target_init
        request_target = "fn.ping_"
    else:
        unknown_target = None
        request_target = request_target_init

    function_type = cast(VFn, parsed_u_api_schema[request_target])
    result_union_type: VUnion = function_type.result

    call_id = request_headers.get("id_")
    if call_id is not None:
        response_headers["id_"] = call_id

    if "_parseFailures" in request_headers:
        parse_failures = cast(list[object], request_headers["_parseFailures"])
        new_error_result: dict[str, object] = {
            "ErrorParseFailure_": {"reasons": parse_failures}
        }

        validate_result(result_union_type, new_error_result)

        return Message(response_headers, new_error_result)

    request_header_validation_failures: list[ValidationFailure] = validate_headers(
        request_headers, u_api_schema.parsed_request_headers, function_type
    )
    if request_header_validation_failures:
        return get_invalid_error_message(
            "ErrorInvalidRequestHeaders_",
            request_header_validation_failures,
            result_union_type,
            response_headers,
        )

    if "bin_" in request_headers:
        client_known_binary_checksums = cast(
            list[object], request_headers["bin_"])

        response_headers["_binary"] = True
        response_headers["_clientKnownBinaryChecksums"] = client_known_binary_checksums

        if "pac_" in request_headers:
            response_headers["pac_"] = request_headers["pac_"]

    select_struct_fields_header: dict[str, object] | None = cast(dict[str, object] | None, request_headers.get(
        "select_"
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

    function_type_call: VUnion = function_type.call

    call_validation_failures: list[ValidationFailure] = function_type_call.validate(
        request_body, [], ValidateContext(None, None)
    )
    if call_validation_failures:
        return get_invalid_error_message(
            "ErrorInvalidRequestBody_",
            call_validation_failures,
            result_union_type,
            response_headers,
        )

    unsafe_response_enabled = cast(bool, request_headers.get("unsafe_", False))

    call_message: Message = Message(
        request_headers, {request_target: request_payload})

    result_message: Message
    if request_target == "fn.ping_":
        result_message = Message({}, {"Ok_": {}})
    elif request_target == "fn.api_":
        result_message = Message({}, {"Ok_": {"api": u_api_schema.original}})
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
        result_validation_failures: list[ValidationFailure] = result_union_type.validate(
            result_union, [], ValidateContext(
                select_struct_fields_header, function_type.name)
        )
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
            final_response_headers, u_api_schema.parsed_response_headers, function_type
        )
        if response_header_validation_failures:
            return get_invalid_error_message(
                "ErrorInvalidResponseHeaders_",
                response_header_validation_failures,
                result_union_type,
                response_headers,
            )

    final_result_union: dict[str, object]
    if select_struct_fields_header is not None:
        final_result_union = cast(dict[str, object], select_struct_fields(
            VTypeDeclaration(result_union_type, False, []),
            result_union,
            select_struct_fields_header,
        ))
    else:
        final_result_union = result_union

    return Message(final_response_headers, final_result_union)
