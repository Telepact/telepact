package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Function;

class _ServerHandlerUtil {

    static Message handleMessage(Message requestMessage, UApiSchema uApiSchema, Function<Message, Message> handler,
            Consumer<Throwable> onError) {
        final var responseHeaders = (Map<String, Object>) new HashMap<String, Object>();
        final Map<String, Object> requestHeaders = requestMessage.header;
        final Map<String, Object> requestBody = requestMessage.body;
        final Map<String, _UType> parsedUApiSchema = uApiSchema.parsed;
        final Map.Entry<String, Object> requestEntry = _Util.entry(requestBody);

        final String requestTargetInit;
        final Map<String, Object> requestPayload;
        if (requestEntry != null) {
            requestTargetInit = requestEntry.getKey();
            requestPayload = (Map<String, Object>) requestEntry.getValue();
        } else {
            requestTargetInit = "fn._unknown";
            requestPayload = Map.of();
        }

        final String unknownTarget;
        final String requestTarget;
        if (!parsedUApiSchema.containsKey(requestTargetInit)) {
            unknownTarget = requestTargetInit;
            requestTarget = "fn._unknown";
        } else {
            unknownTarget = null;
            requestTarget = requestTargetInit;
        }

        final var functionType = (_UFn) parsedUApiSchema.get(requestTarget);
        final var resultUnionType = functionType.result;

        final var callId = requestHeaders.get("_id");
        if (callId != null) {
            responseHeaders.put("_id", callId);
        }

        if (requestHeaders.containsKey("_parseFailures")) {
            final var parseFailures = (List<Object>) requestHeaders.get("_parseFailures");
            final Map<String, Object> newErrorResult = Map.of("_ErrorParseFailure",
                    Map.of("reasons", parseFailures));

            validateResult(resultUnionType, newErrorResult);

            return new Message(responseHeaders, newErrorResult);
        }

        final List<_Util._ValidationFailure> headerValidationFailures = _ValidateUtil.validateHeaders(requestHeaders,
                uApiSchema, functionType);
        if (!headerValidationFailures.isEmpty()) {
            return getInvalidErrorMessage("_ErrorInvalidRequestHeaders", headerValidationFailures, resultUnionType,
                    responseHeaders);
        }

        if (requestHeaders.containsKey("_bin")) {
            final List<Object> clientKnownBinaryChecksums = (List<Object>) requestHeaders.get("_bin");

            responseHeaders.put("_binary", true);
            responseHeaders.put("_clientKnownBinaryChecksums", clientKnownBinaryChecksums);

            if (requestHeaders.containsKey("_pac")) {
                responseHeaders.put("_pac", requestHeaders.get("_pac"));
            }
        }

        if (unknownTarget != null) {
            final Map<String, Object> newErrorResult = Map.of("_ErrorInvalidRequestBody",
                    Map.of("cases",
                            List.of(Map.of("path", List.of(unknownTarget), "reason",
                                    Map.of("FunctionUnknown", Map.of())))));

            validateResult(resultUnionType, newErrorResult);
            return new Message(responseHeaders, newErrorResult);
        }

        final _UUnion functionTypeCall = functionType.call;

        final var callValidationFailures = functionTypeCall.validate(requestBody, List.of(), List.of());
        if (!callValidationFailures.isEmpty()) {
            return getInvalidErrorMessage("_ErrorInvalidRequestBody", callValidationFailures, resultUnionType,
                    responseHeaders);
        }

        final var unsafeResponseEnabled = Objects.equals(true, requestHeaders.get("_unsafe"));

        final var callMessage = new Message(requestHeaders, Map.of(requestTarget, requestPayload));

        final Message resultMessage;
        if (requestTarget.equals("fn._ping")) {
            resultMessage = new Message("Ok", Map.of());
        } else if (requestTarget.equals("fn._api")) {
            resultMessage = new Message("Ok", Map.of("api", uApiSchema.original));
        } else {
            try {
                resultMessage = handler.apply(callMessage);
            } catch (Throwable e) {
                try {
                    onError.accept(e);
                } catch (Throwable ignored) {

                }
                return new Message(responseHeaders, Map.of("_ErrorUnknown", Map.of()));
            }
        }

        final var skipResultValidation = unsafeResponseEnabled;
        if (!skipResultValidation) {
            final var resultValidationFailures = resultUnionType.validate(
                    resultMessage.body, List.of(), List.of());
            if (!resultValidationFailures.isEmpty()) {
                return getInvalidErrorMessage("_ErrorInvalidResponseBody", resultValidationFailures, resultUnionType,
                        responseHeaders);
            }
        }

        final Map<String, Object> resultUnion = resultMessage.body;

        resultMessage.header.putAll(responseHeaders);
        final Map<String, Object> finalResponseHeaders = resultMessage.header;

        final Map<String, Object> finalResultUnion;
        if (requestHeaders.containsKey("_sel")) {
            Map<String, Object> selectStructFieldsHeader = (Map<String, Object>) requestHeaders
                    .get("_sel");
            finalResultUnion = (Map<String, Object>) _SelectUtil.selectStructFields(
                    new _UTypeDeclaration(resultUnionType, false, List.of()),
                    resultUnion,
                    selectStructFieldsHeader);
        } else {
            finalResultUnion = resultUnion;
        }

        return new Message(finalResponseHeaders, finalResultUnion);
    }

    private static Message getInvalidErrorMessage(String error, List<_Util._ValidationFailure> validationFailures,
            _UUnion resultUnionType, Map<String, Object> responseHeaders) {
        final var validationFailureCases = mapValidationFailuresToInvalidFieldCases(validationFailures);
        final Map<String, Object> newErrorResult = Map.of(error,
                Map.of("cases", validationFailureCases));

        validateResult(resultUnionType, newErrorResult);
        return new Message(responseHeaders, newErrorResult);
    }

    private static List<Map<String, Object>> mapValidationFailuresToInvalidFieldCases(
            List<_Util._ValidationFailure> argumentValidationFailures) {
        final var validationFailureCases = new ArrayList<Map<String, Object>>();
        for (final var validationFailure : argumentValidationFailures) {
            final Map<String, Object> validationFailureCase = Map.of(
                    "path", validationFailure.path,
                    "reason", Map.of(validationFailure.reason, validationFailure.data));
            validationFailureCases.add(validationFailureCase);
        }

        return validationFailureCases;
    }

    private static void validateResult(_UUnion resultUnionType, Object errorResult) {
        final var newErrorResultValidationFailures = resultUnionType.validate(
                errorResult, List.of(), List.of());
        if (!newErrorResultValidationFailures.isEmpty()) {
            throw new UApiProcessError(
                    "Failed internal uAPI validation: "
                            + mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures));
        }
    }

}
