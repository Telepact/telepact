//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact.internal;

import static io.github.telepact.internal.SelectStructFields.selectStructFields;
import static io.github.telepact.internal.validation.GetInvalidErrorMessage.getInvalidErrorMessage;
import static io.github.telepact.internal.validation.ValidateHeaders.validateHeaders;
import static io.github.telepact.internal.validation.ValidateResult.validateResult;
import static io.github.telepact.internal.binary.ServerBase64Decode.serverBase64Decode;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Function;

import io.github.telepact.Message;
import io.github.telepact.TelepactSchema;
import io.github.telepact.internal.types.TType;
import io.github.telepact.internal.types.TTypeDeclaration;
import io.github.telepact.internal.types.TUnion;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class HandleMessage {
    static Message handleMessage(Message requestMessage, TelepactSchema telepactSchema, Function<Message, Message> handler,
            Consumer<Throwable> onError) {
        final var responseHeaders = (Map<String, Object>) new HashMap<String, Object>();
        final Map<String, Object> requestHeaders = requestMessage.headers;
        final Map<String, Object> requestBody = requestMessage.body;
        final Map<String, TType> parsedTelepactSchema = telepactSchema.parsed;
        final Map.Entry<String, Object> requestEntry = requestBody.entrySet().stream().findAny().get();

        final String requestTargetInit = requestEntry.getKey();
        final Map<String, Object> requestPayload = (Map<String, Object>) requestEntry.getValue();

        final String unknownTarget;
        final String requestTarget;
        if (!parsedTelepactSchema.containsKey(requestTargetInit)) {
            unknownTarget = requestTargetInit;
            requestTarget = "fn.ping_";
        } else {
            unknownTarget = null;
            requestTarget = requestTargetInit;
        }

        final var functionName = requestTarget;
        final var callType = (TUnion) parsedTelepactSchema.get(requestTarget);
        final var resultUnionType = (TUnion) parsedTelepactSchema.get(requestTarget + ".->");

        final var callId = requestHeaders.get("@id_");
        if (callId != null) {
            responseHeaders.put("@id_", callId);
        }

        if (requestHeaders.containsKey("_parseFailures")) {
            final var parseFailures = (List<Object>) requestHeaders.get("_parseFailures");
            final Map<String, Object> newErrorResult = Map.of("ErrorParseFailure_",
                    Map.of("reasons", parseFailures));

            validateResult(resultUnionType, newErrorResult);

            return new Message(responseHeaders, newErrorResult);
        }

        final List<ValidationFailure> requestHeaderValidationFailures = validateHeaders(requestHeaders,
                telepactSchema.parsedRequestHeaders, functionName);
        if (!requestHeaderValidationFailures.isEmpty()) {
            return getInvalidErrorMessage("ErrorInvalidRequestHeaders_", requestHeaderValidationFailures,
                    resultUnionType,
                    responseHeaders);
        }

        if (requestHeaders.containsKey("@bin_")) {
            final List<Object> clientKnownBinaryChecksums = (List<Object>) requestHeaders.get("@bin_");

            responseHeaders.put("@binary_", true);
            responseHeaders.put("@clientKnownBinaryChecksums_", clientKnownBinaryChecksums);

            if (requestHeaders.containsKey("@pac_")) {
                responseHeaders.put("@pac_", requestHeaders.get("@pac_"));
            }
        }

        final Map<String, Object> selectStructFieldsHeader = (Map<String, Object>) requestHeaders.get("@select_");

        if (unknownTarget != null) {
            final Map<String, Object> newErrorResult = Map.of("ErrorInvalidRequestBody_",
                    Map.of("cases",
                            List.of(Map.of("path", List.of(unknownTarget), "reason",
                                    Map.of("FunctionUnknown", Map.of())))));

            validateResult(resultUnionType, newErrorResult);
            return new Message(responseHeaders, newErrorResult);
        }

        final TUnion functionTypeCall = callType;

        final var callValidateCtx = new ValidateContext(null, null, false);

        final var callValidationFailures = functionTypeCall.validate(requestBody, List.of(),
                callValidateCtx);
        if (!callValidationFailures.isEmpty()) {
            return getInvalidErrorMessage("ErrorInvalidRequestBody_", callValidationFailures, resultUnionType,
                    responseHeaders);
        }

        if (callValidateCtx.bytesCoercions.size() > 0) {
            serverBase64Decode(requestBody, callValidateCtx.bytesCoercions);
        }

        final var unsafeResponseEnabled = Objects.equals(true, requestHeaders.get("@unsafe_"));

        final var callMessage = new Message(requestHeaders, Map.of(requestTarget, requestPayload));

        final Message resultMessage;
        if (functionName.equals("fn.ping_")) {
            resultMessage = new Message(Map.of(), Map.of("Ok_", Map.of()));
        } else if (functionName.equals("fn.api_")) {
            resultMessage = new Message(Map.of(), Map.of("Ok_", Map.of("api", telepactSchema.original)));
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

        final var coerceBase64 = !Objects.equals(true, requestHeaders.get("@binary_"));
        final var resultValidateCtx = new ValidateContext(selectStructFieldsHeader, requestTarget, coerceBase64);
        
        final var resultValidationFailures = resultUnionType.validate(resultUnion, List.of(), resultValidateCtx);
        if (!resultValidationFailures.isEmpty() && !skipResultValidation) {
            return getInvalidErrorMessage("ErrorInvalidResponseBody_", resultValidationFailures, resultUnionType,
                    finalResponseHeaders);
        }
        
        if (!resultValidateCtx.base64Coercions.isEmpty()) {
            finalResponseHeaders.put("@base64_", resultValidateCtx.base64Coercions);
        }

        if (resultValidateCtx.bytesCoercions.size() > 0) {
            serverBase64Decode(resultUnion, resultValidateCtx.bytesCoercions);
        }
        
        final List<ValidationFailure> responseHeaderValidationFailures = validateHeaders(finalResponseHeaders,
                telepactSchema.parsedResponseHeaders, functionName);
        if (!responseHeaderValidationFailures.isEmpty()) {
            return getInvalidErrorMessage("ErrorInvalidResponseHeaders_", responseHeaderValidationFailures,
                    resultUnionType,
                    responseHeaders);
        }

        final Map<String, Object> finalResultUnion;
        if (selectStructFieldsHeader != null) {
            finalResultUnion = (Map<String, Object>) selectStructFields(
                    new TTypeDeclaration(resultUnionType, false, List.of()),
                    resultUnion,
                    selectStructFieldsHeader);
        } else {
            finalResultUnion = resultUnion;
        }

        return new Message(finalResponseHeaders, finalResultUnion);
    }
}
