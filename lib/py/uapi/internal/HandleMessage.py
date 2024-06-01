from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from uapi import Message, UApiSchema
from uapi.internal.types import UFn, UType, UTypeDeclaration, UUnion

from uapi.internal.validation import (
    getInvalidErrorMessage,
    selectStructFields,
    validateHeaders,
    validateResult,
    ValidationFailure,
)


def handleMessage(
    requestMessage: Message,
    uApiSchema: UApiSchema,
    handler: Callable[[Message], Message],
    onError: Callable[[Exception], None],
) -> Message:
    responseHeaders: Dict[str, Any] = {}
    requestHeaders: Dict[str, Any] = requestMessage.header
    requestBody: Dict[str, Any] = requestMessage.body
    parsedUApiSchema: Dict[str, UType] = uApiSchema.parsed
    requestEntry: Tuple[str, Any] = next(iter(requestBody.items()))

    requestTargetInit: str = requestEntry[0]
    requestPayload: Dict[str, Any] = requestEntry[1]

    unknownTarget: Optional[str]
    requestTarget: str
    if requestTargetInit not in parsedUApiSchema:
        unknownTarget = requestTargetInit
        requestTarget = "fn.ping_"
    else:
        unknownTarget = None
        requestTarget = requestTargetInit

    functionType: UFn = parsedUApiSchema[requestTarget]
    resultUnionType: UUnion = functionType.result

    callId = requestHeaders.get("id_")
    if callId is not None:
        responseHeaders["id_"] = callId

    if "_parseFailures" in requestHeaders:
        parseFailures: List[Any] = requestHeaders["_parseFailures"]
        newErrorResult: Dict[str, Any] = {
            "ErrorParseFailure_": {"reasons": parseFailures}
        }

        validateResult(resultUnionType, newErrorResult)

        return Message(responseHeaders, newErrorResult)

    requestHeaderValidationFailures: List[ValidationFailure] = validateHeaders(
        requestHeaders, uApiSchema.parsedRequestHeaders, functionType
    )
    if requestHeaderValidationFailures:
        return getInvalidErrorMessage(
            "ErrorInvalidRequestHeaders_",
            requestHeaderValidationFailures,
            resultUnionType,
            responseHeaders,
        )

    if "bin_" in requestHeaders:
        clientKnownBinaryChecksums: List[Any] = requestHeaders["bin_"]

        responseHeaders["_binary"] = True
        responseHeaders["_clientKnownBinaryChecksums"] = clientKnownBinaryChecksums

        if "_pac" in requestHeaders:
            responseHeaders["_pac"] = requestHeaders["_pac"]

    selectStructFieldsHeader: Optional[Dict[str, Any]] = requestHeaders.get(
        "select_")

    if unknownTarget is not None:
        newErrorResult: Dict[str, Any] = {
            "ErrorInvalidRequestBody_": {
                "cases": [
                    {
                        "path": [unknownTarget],
                        "reason": {"FunctionUnknown": {}},
                    }
                ]
            }
        }

        validateResult(resultUnionType, newErrorResult)
        return Message(responseHeaders, newErrorResult)

    functionTypeCall: UUnion = functionType.call

    callValidationFailures: List[ValidationFailure] = functionTypeCall.validate(
        requestBody, None, None, [], []
    )
    if callValidationFailures:
        return getInvalidErrorMessage(
            "ErrorInvalidRequestBody_",
            callValidationFailures,
            resultUnionType,
            responseHeaders,
        )

    unsafeResponseEnabled: bool = requestHeaders.get("unsafe_", False)

    callMessage: Message = Message(
        requestHeaders, {requestTarget: requestPayload})

    resultMessage: Message
    if requestTarget == "fn.ping_":
        resultMessage = Message({}, {"Ok_": {}})
    elif requestTarget == "fn.api_":
        resultMessage = Message({}, {"Ok_": {"api": uApiSchema.original}})
    else:
        try:
            resultMessage = handler(callMessage)
        except Exception as e:
            try:
                onError(e)
            except Exception:
                pass
            return Message(responseHeaders, {"ErrorUnknown_": {}})

    resultUnion: Dict[str, Any] = resultMessage.body

    resultMessage.header.update(responseHeaders)
    finalResponseHeaders: Dict[str, Any] = resultMessage.header

    skipResultValidation: bool = unsafeResponseEnabled
    if not skipResultValidation:
        resultValidationFailures: List[ValidationFailure] = resultUnionType.validate(
            resultUnion, selectStructFieldsHeader, None, [], []
        )
        if resultValidationFailures:
            return getInvalidErrorMessage(
                "ErrorInvalidResponseBody_",
                resultValidationFailures,
                resultUnionType,
                responseHeaders,
            )
        responseHeaderValidationFailures: List[ValidationFailure] = validateHeaders(
            finalResponseHeaders, uApiSchema.parsedResponseHeaders, functionType
        )
        if responseHeaderValidationFailures:
            return getInvalidErrorMessage(
                "ErrorInvalidResponseHeaders_",
                responseHeaderValidationFailures,
                resultUnionType,
                responseHeaders,
            )

    finalResultUnion: Dict[str, Any]
    if selectStructFieldsHeader is not None:
        finalResultUnion = selectStructFields(
            UTypeDeclaration(resultUnionType, False, []),
            resultUnion,
            selectStructFieldsHeader,
        )
    else:
        finalResultUnion = resultUnion

    return Message(finalResponseHeaders, finalResultUnion)
