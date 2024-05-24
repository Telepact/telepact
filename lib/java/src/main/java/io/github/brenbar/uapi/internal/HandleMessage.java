package io.github.brenbar.uapi.internal;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Function;

import io.github.brenbar.uapi.Message;
import io.github.brenbar.uapi.UApiSchema;

import static io.github.brenbar.uapi.internal.SelectStructFields.selectStructFields;
import static io.github.brenbar.uapi.internal.UnionEntry.unionEntry;
import static io.github.brenbar.uapi.internal.ValidateHeaders.validateHeaders;
import static io.github.brenbar.uapi.internal.ValidateResult.validateResult;
import static io.github.brenbar.uapi.internal.GetInvalidErrorMessage.getInvalidErrorMessage;

public class HandleMessage {
    static Message handleMessage(Message requestMessage, UApiSchema uApiSchema, Function<Message, Message> handler,
            Consumer<Throwable> onError) {
        final var responseHeaders = (Map<String, Object>) new HashMap<String, Object>();
        final Map<String, Object> requestHeaders = requestMessage.header;
        final Map<String, Object> requestBody = requestMessage.body;
        final Map<String, UType> parsedUApiSchema = uApiSchema.parsed;
        final Map.Entry<String, Object> requestEntry = unionEntry(requestBody);

        final String requestTargetInit = requestEntry.getKey();
        final Map<String, Object> requestPayload = (Map<String, Object>) requestEntry.getValue();

        final String unknownTarget;
        final String requestTarget;
        if (!parsedUApiSchema.containsKey(requestTargetInit)) {
            unknownTarget = requestTargetInit;
            requestTarget = "fn.ping_";
        } else {
            unknownTarget = null;
            requestTarget = requestTargetInit;
        }

        final var functionType = (UFn) parsedUApiSchema.get(requestTarget);
        final var resultUnionType = functionType.result;

        final var callId = requestHeaders.get("id_");
        if (callId != null) {
            responseHeaders.put("id_", callId);
        }

        if (requestHeaders.containsKey("_parseFailures")) {
            final var parseFailures = (List<Object>) requestHeaders.get("_parseFailures");
            final Map<String, Object> newErrorResult = Map.of("ErrorParseFailure_",
                    Map.of("reasons", parseFailures));

            validateResult(resultUnionType, newErrorResult);

            return new Message(responseHeaders, newErrorResult);
        }

        final List<ValidationFailure> requestHeaderValidationFailures = validateHeaders(requestHeaders,
                uApiSchema.parsedRequestHeaders, functionType);
        if (!requestHeaderValidationFailures.isEmpty()) {
            return getInvalidErrorMessage("ErrorInvalidRequestHeaders_", requestHeaderValidationFailures,
                    resultUnionType,
                    responseHeaders);
        }

        if (requestHeaders.containsKey("bin_")) {
            final List<Object> clientKnownBinaryChecksums = (List<Object>) requestHeaders.get("bin_");

            responseHeaders.put("_binary", true);
            responseHeaders.put("_clientKnownBinaryChecksums", clientKnownBinaryChecksums);

            if (requestHeaders.containsKey("_pac")) {
                responseHeaders.put("_pac", requestHeaders.get("_pac"));
            }
        }

        final Map<String, Object> selectStructFieldsHeader = (Map<String, Object>) requestHeaders.get("select_");

        if (unknownTarget != null) {
            final Map<String, Object> newErrorResult = Map.of("ErrorInvalidRequestBody_",
                    Map.of("cases",
                            List.of(Map.of("path", List.of(unknownTarget), "reason",
                                    Map.of("FunctionUnknown", Map.of())))));

            validateResult(resultUnionType, newErrorResult);
            return new Message(responseHeaders, newErrorResult);
        }

        final UUnion functionTypeCall = functionType.call;

        final var callValidationFailures = functionTypeCall.validate(requestBody, null, null, List.of(), List.of());
        if (!callValidationFailures.isEmpty()) {
            return getInvalidErrorMessage("ErrorInvalidRequestBody_", callValidationFailures, resultUnionType,
                    responseHeaders);
        }

        final var unsafeResponseEnabled = Objects.equals(true, requestHeaders.get("unsafe_"));

        final var callMessage = new Message(requestHeaders, Map.of(requestTarget, requestPayload));

        final Message resultMessage;
        if (requestTarget.equals("fn.ping_")) {
            resultMessage = new Message(Map.of(), Map.of("Ok_", Map.of()));
        } else if (requestTarget.equals("fn.api_")) {
            resultMessage = new Message(Map.of(), Map.of("Ok_", Map.of("api", uApiSchema.original)));
        } else {
            try {
                resultMessage = handler.apply(callMessage);
            } catch (Throwable e) {
                try {
                    onError.accept(e);
                } catch (Throwable ignored) {

                }
                return new Message(responseHeaders, Map.of("ErrorUnknown_", Map.of()));
            }
        }

        final Map<String, Object> resultUnion = resultMessage.body;

        resultMessage.header.putAll(responseHeaders);
        final Map<String, Object> finalResponseHeaders = resultMessage.header;

        final var skipResultValidation = unsafeResponseEnabled;
        if (!skipResultValidation) {
            final var resultValidationFailures = resultUnionType.validate(
                    resultUnion, selectStructFieldsHeader, null, List.of(), List.of());
            if (!resultValidationFailures.isEmpty()) {
                return getInvalidErrorMessage("ErrorInvalidResponseBody_", resultValidationFailures, resultUnionType,
                        responseHeaders);
            }
            final List<ValidationFailure> responseHeaderValidationFailures = validateHeaders(finalResponseHeaders,
                    uApiSchema.parsedResponseHeaders, functionType);
            if (!responseHeaderValidationFailures.isEmpty()) {
                return getInvalidErrorMessage("ErrorInvalidResponseHeaders_", responseHeaderValidationFailures,
                        resultUnionType,
                        responseHeaders);
            }
        }

        final Map<String, Object> finalResultUnion;
        if (selectStructFieldsHeader != null) {
            finalResultUnion = (Map<String, Object>) selectStructFields(
                    new UTypeDeclaration(resultUnionType, false, List.of()),
                    resultUnion,
                    selectStructFieldsHeader);
        } else {
            finalResultUnion = resultUnion;
        }

        return new Message(finalResponseHeaders, finalResultUnion);
    }
}
