package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Function;

class _ServerHandlerUtil {

    static Message handleMessage(Message requestMessage,
            JApiSchema jApiSchema,
            Function<Message, Message> handler,
            Consumer<Throwable> onError) {
        boolean unsafeResponseEnabled = false;
        var responseHeaders = (Map<String, Object>) new HashMap<String, Object>();
        var requestHeaders = requestMessage.header;
        var requestBody = requestMessage.body;
        var requestEntry = _UUnion.entry(requestBody);
        String requestTarget;
        Map<String, Object> requestPayload;
        if (requestEntry != null) {
            requestTarget = requestEntry.getKey();
            requestPayload = (Map<String, Object>) requestEntry.getValue();
        } else {
            requestTarget = "fn._unknown";
            requestPayload = Map.of();
        }
        var unknownTarget = (String) null;
        if (!jApiSchema.parsed.containsKey(requestTarget)) {
            unknownTarget = requestTarget;
            requestTarget = "fn._unknown";
        }
        var functionType = (_UFn) jApiSchema.parsed.get(requestTarget);
        var resultUnionType = functionType.result;

        var callId = requestHeaders.get("_id");
        if (callId != null) {
            responseHeaders.put("_id", callId);
        }

        if (requestHeaders.containsKey("_parseFailures")) {
            var parseFailures = (List<Object>) requestHeaders.get("_parseFailures");
            Map<String, Object> newErrorResult = Map.of("_ErrorParseFailure",
                    Map.of("reasons", parseFailures));
            validateResult(resultUnionType, newErrorResult);

            return new Message(responseHeaders, newErrorResult);
        }

        var headerValidationFailures = _ValidateUtil.validateHeaders(requestHeaders, jApiSchema, functionType);

        if (!headerValidationFailures.isEmpty()) {
            return getInvalidErrorMessage("_ErrorInvalidRequestHeaders", headerValidationFailures, resultUnionType,
                    responseHeaders);
        }

        if (requestHeaders.containsKey("_bin")) {
            List<Object> clientKnownBinaryChecksums = (List<Object>) requestHeaders.get("_bin");
            responseHeaders.put("_binary", true);
            responseHeaders.put("_clientKnownBinaryChecksums", clientKnownBinaryChecksums);
            if (requestHeaders.containsKey("_pac")) {
                responseHeaders.put("_pac", requestHeaders.get("_pac"));
            }
        }

        if (unknownTarget != null) {
            Map<String, Object> newErrorResult = Map.of("_ErrorInvalidRequestBody",
                    Map.of("cases",
                            List.of(Map.of("path", List.of(unknownTarget), "reason",
                                    Map.of("FunctionUnknown", Map.of())))));
            validateResult(resultUnionType, newErrorResult);
            return new Message(responseHeaders, newErrorResult);
        }

        var callValidationFailures = functionType.call.validate(requestBody, List.of(), List.of());
        if (!callValidationFailures.isEmpty()) {
            return getInvalidErrorMessage("_ErrorInvalidRequestBody", callValidationFailures, resultUnionType,
                    responseHeaders);
        }

        unsafeResponseEnabled = Objects.equals(true, requestHeaders.get("_unsafe"));

        var callMessage = new Message(requestHeaders, Map.of(requestTarget, requestPayload));

        Message resultMessage;
        if (requestTarget.equals("fn._ping")) {
            resultMessage = new Message("Ok", Map.of());
        } else if (requestTarget.equals("fn._api")) {
            resultMessage = new Message("Ok", Map.of("api", jApiSchema.original));
        } else {
            try {
                resultMessage = handler.apply(callMessage);
            } catch (Throwable e) {
                try {
                    onError.accept(e);
                } catch (Throwable ignored) {

                }
                resultMessage = new Message("_ErrorUnknown", Map.of());
            }
        }
        var skipResultValidation = unsafeResponseEnabled;
        if (!skipResultValidation) {
            var resultValidationFailures = resultUnionType.validate(
                    resultMessage.body, List.of(), List.of());
            if (!resultValidationFailures.isEmpty()) {
                return getInvalidErrorMessage("_ErrorInvalidResponseBody", resultValidationFailures, resultUnionType,
                        responseHeaders);
            }
        }

        Map<String, Object> resultUnion = resultMessage.body;
        resultMessage.header.putAll(responseHeaders);
        responseHeaders = resultMessage.header;

        Map<String, Object> finalResultUnion;
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

        return new Message(responseHeaders, finalResultUnion);
    }

    private static Message getInvalidErrorMessage(String error, List<ValidationFailure> validationFailures,
            _UUnion resultUnionType, Map<String, Object> responseHeaders) {
        var validationFailureCases = mapValidationFailuresToInvalidFieldCases(validationFailures);
        Map<String, Object> newErrorResult = Map.of(error,
                Map.of("cases", validationFailureCases));
        validateResult(resultUnionType, newErrorResult);
        return new Message(responseHeaders, newErrorResult);
    }

    private static List<Map<String, Object>> mapValidationFailuresToInvalidFieldCases(
            List<ValidationFailure> argumentValidationFailures) {
        var validationFailureCases = new ArrayList<Map<String, Object>>();
        for (var validationFailure : argumentValidationFailures) {
            Map<String, Object> validationFailureCase = Map.of(
                    "path", validationFailure.path,
                    "reason", Map.of(validationFailure.reason, validationFailure.data));
            validationFailureCases.add(validationFailureCase);
        }
        return validationFailureCases;
    }

    private static void validateResult(_UUnion resultUnionType, Object errorResult) {
        var newErrorResultValidationFailures = resultUnionType.validate(
                errorResult, List.of(), List.of());
        if (!newErrorResultValidationFailures.isEmpty()) {
            throw new JApiProcessError(
                    "Failed internal jAPI validation: "
                            + mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures));
        }
    }

}
