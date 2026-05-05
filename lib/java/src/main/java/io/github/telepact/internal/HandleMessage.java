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
import static io.github.telepact.internal.UnknownError.buildUnknownErrorMessage;
import static io.github.telepact.internal.validation.GetInvalidErrorMessage.getInvalidErrorMessage;
import static io.github.telepact.internal.validation.MapValidationFailuresToInvalidFieldCases.mapValidationFailuresToInvalidFieldCases;
import static io.github.telepact.internal.validation.ValidateHeaders.validateHeaders;
import static io.github.telepact.internal.validation.ValidateResult.validateResult;
import static io.github.telepact.internal.binary.ServerBase64Decode.serverBase64Decode;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.function.Consumer;

import io.github.telepact.FunctionRouter;
import io.github.telepact.Message;
import io.github.telepact.Server.AuthHandler;
import io.github.telepact.Server.Middleware;
import io.github.telepact.TelepactError;
import io.github.telepact.TelepactSchema;
import io.github.telepact.internal.types.TType;
import io.github.telepact.internal.types.TTypeDeclaration;
import io.github.telepact.internal.types.TUnion;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class HandleMessage {
    private static final String UNAUTHENTICATED_MESSAGE = "Valid authentication is required.";

    static Message handleMessage(Message requestMessage, Consumer<Map<String, Object>> updateHeaders, TelepactSchema telepactSchema, Middleware middleware,
            FunctionRouter functionRouter,
            Consumer<TelepactError> onError, AuthHandler onAuth) {
        final var responseHeaders = (Map<String, Object>) new HashMap<String, Object>();
        final Map<String, Object> requestHeaders = requestMessage.headers;
        final Map<String, Object> requestBody = requestMessage.body;
        final Map<String, TType> parsedTelepactSchema = telepactSchema.parsed;
        final Map.Entry<String, Object> requestEntry = requestBody.entrySet().stream().findAny().get();

        if (updateHeaders != null) {
            updateHeaders.accept(requestHeaders);
        }

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
        final var requiresAuthentication = unknownTarget == null && functionRouter.requiresAuthentication(functionName);

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

        if (requiresAuthentication && !requestHeaders.containsKey("@auth_")) {
            return buildUnauthenticatedErrorMessage(resultUnionType, responseHeaders);
        }

        if (requiresAuthentication) {
            try {
                final var authFuture = onAuth.apply(requestHeaders);
                final var authHeaders = authFuture == null ? Map.<String, Object>of() : authFuture.get();
                if (authHeaders != null) {
                    requestHeaders.putAll(authHeaders);
                }
            } catch (Throwable e) {
                if (e instanceof InterruptedException) {
                    Thread.currentThread().interrupt();
                }
                final var wrapped = new TelepactError(
                        "telepact auth handler failed while handling %s".formatted(functionName),
                        "handler",
                        e);
                try {
                    onError.accept(wrapped);
                } catch (Throwable ignored) {
                }
                return buildUnauthenticatedErrorMessage(resultUnionType, responseHeaders);
            }
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
        try {
            resultMessage = middleware.apply(callMessage, functionRouter);
        } catch (Throwable e) {
            final var wrapped = new TelepactError(
                    "telepact handler failed while handling %s".formatted(functionName),
                    "handler",
                    e);
            try {
                onError.accept(wrapped);
            } catch (Throwable ignored) {

            }
            return buildUnknownErrorMessage(wrapped, responseHeaders);
        }

        final Map<String, Object> resultUnion = resultMessage.body;

        resultMessage.headers.putAll(responseHeaders);
        final Map<String, Object> finalResponseHeaders = resultMessage.headers;

        final var skipResultValidation = unsafeResponseEnabled;

        final var coerceBase64 = !Objects.equals(true, requestHeaders.get("@binary_"));
        final var resultValidateCtx = new ValidateContext(selectStructFieldsHeader, requestTarget, coerceBase64);
        
        final var resultValidationFailures = resultUnionType.validate(resultUnion, List.of(), resultValidateCtx);
        if (!resultValidationFailures.isEmpty() && !skipResultValidation) {
            try {
                onError.accept(new TelepactError(
                        "telepact response validation failed for %s: %s".formatted(
                                functionName,
                                mapValidationFailuresToInvalidFieldCases(resultValidationFailures)),
                        "validation"));
            } catch (Throwable ignored) {
            }
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
            try {
                onError.accept(new TelepactError(
                        "telepact response header validation failed for %s: %s".formatted(
                                functionName,
                                mapValidationFailuresToInvalidFieldCases(responseHeaderValidationFailures)),
                        "validation"));
            } catch (Throwable ignored) {
            }
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

    private static Message buildUnauthenticatedErrorMessage(TUnion resultUnionType, Map<String, Object> headers) {
        final Map<String, Object> result = Map.of(
                "ErrorUnauthenticated_",
                Map.of("message!", UNAUTHENTICATED_MESSAGE));
        validateResult(resultUnionType, result);
        return new Message(headers, result);
    }
}
