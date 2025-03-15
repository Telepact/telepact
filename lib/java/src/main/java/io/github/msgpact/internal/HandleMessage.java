package io.github.msgpact.internal;

import static io.github.msgpact.internal.SelectStructFields.selectStructFields;
import static io.github.msgpact.internal.validation.GetInvalidErrorMessage.getInvalidErrorMessage;
import static io.github.msgpact.internal.validation.ValidateHeaders.validateHeaders;
import static io.github.msgpact.internal.validation.ValidateResult.validateResult;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Function;

import io.github.msgpact.Message;
import io.github.msgpact.MsgPactSchema;
import io.github.msgpact.internal.types.VFn;
import io.github.msgpact.internal.types.VType;
import io.github.msgpact.internal.types.VTypeDeclaration;
import io.github.msgpact.internal.types.VUnion;
import io.github.msgpact.internal.validation.ValidateContext;
import io.github.msgpact.internal.validation.ValidationFailure;

public class HandleMessage {
    static Message handleMessage(Message requestMessage, MsgPactSchema msgPactSchema, Function<Message, Message> handler,
            Consumer<Throwable> onError) {
        final var responseHeaders = (Map<String, Object>) new HashMap<String, Object>();
        final Map<String, Object> requestHeaders = requestMessage.headers;
        final Map<String, Object> requestBody = requestMessage.body;
        final Map<String, VType> parsedMsgPactSchema = msgPactSchema.parsed;
        final Map.Entry<String, Object> requestEntry = requestBody.entrySet().stream().findAny().get();

        final String requestTargetInit = requestEntry.getKey();
        final Map<String, Object> requestPayload = (Map<String, Object>) requestEntry.getValue();

        final String unknownTarget;
        final String requestTarget;
        if (!parsedMsgPactSchema.containsKey(requestTargetInit)) {
            unknownTarget = requestTargetInit;
            requestTarget = "fn.ping_";
        } else {
            unknownTarget = null;
            requestTarget = requestTargetInit;
        }

        final var functionType = (VFn) parsedMsgPactSchema.get(requestTarget);
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
                msgPactSchema.parsedRequestHeaders, functionType);
        if (!requestHeaderValidationFailures.isEmpty()) {
            return getInvalidErrorMessage("ErrorInvalidRequestHeaders_", requestHeaderValidationFailures,
                    resultUnionType,
                    responseHeaders);
        }

        if (requestHeaders.containsKey("bin_")) {
            final List<Object> clientKnownBinaryChecksums = (List<Object>) requestHeaders.get("bin_");

            responseHeaders.put("_binary", true);
            responseHeaders.put("_clientKnownBinaryChecksums", clientKnownBinaryChecksums);

            if (requestHeaders.containsKey("pac_")) {
                responseHeaders.put("pac_", requestHeaders.get("pac_"));
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

        final VUnion functionTypeCall = functionType.call;

        final var callValidationFailures = functionTypeCall.validate(requestBody, List.of(),
                new ValidateContext(null, null));
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
            resultMessage = new Message(Map.of(), Map.of("Ok_", Map.of("api", msgPactSchema.original)));
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

        resultMessage.headers.putAll(responseHeaders);
        final Map<String, Object> finalResponseHeaders = resultMessage.headers;

        final var skipResultValidation = unsafeResponseEnabled;
        if (!skipResultValidation) {
            final var resultValidationFailures = resultUnionType.validate(
                    resultUnion, List.of(), new ValidateContext(selectStructFieldsHeader, null));
            if (!resultValidationFailures.isEmpty()) {
                return getInvalidErrorMessage("ErrorInvalidResponseBody_", resultValidationFailures, resultUnionType,
                        responseHeaders);
            }
            final List<ValidationFailure> responseHeaderValidationFailures = validateHeaders(finalResponseHeaders,
                    msgPactSchema.parsedResponseHeaders, functionType);
            if (!responseHeaderValidationFailures.isEmpty()) {
                return getInvalidErrorMessage("ErrorInvalidResponseHeaders_", responseHeaderValidationFailures,
                        resultUnionType,
                        responseHeaders);
            }
        }

        final Map<String, Object> finalResultUnion;
        if (selectStructFieldsHeader != null) {
            finalResultUnion = (Map<String, Object>) selectStructFields(
                    new VTypeDeclaration(resultUnionType, false, List.of()),
                    resultUnion,
                    selectStructFieldsHeader);
        } else {
            finalResultUnion = resultUnion;
        }

        return new Message(finalResponseHeaders, finalResultUnion);
    }
}
