package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Function;

class InternalServer {

    static Message parseRequestMessage(byte[] requestMessageBytes, Serializer serializer, JApiSchemaTuple jApiSchema,
            Consumer<Throwable> onError) {

        Message requestMessage;
        try {
            requestMessage = serializer.deserialize(requestMessageBytes);
        } catch (DeserializationError e) {
            try {
                onError.accept(e);
            } catch (Throwable ignored) {
            }
            var cause = e.getCause();

            List<String> parseFailures;
            if (cause instanceof BinaryEncoderUnavailableError e2) {
                parseFailures = List.of("IncompatibleBinaryEncoding");
            } else if (cause instanceof BinaryEncodingMissing e2) {
                parseFailures = List.of("BinaryDecodeFailure");
            } else if (cause instanceof InvalidJsonError e2) {
                parseFailures = List.of("InvalidJson");
            } else if (cause instanceof MessageParseError e2) {
                parseFailures = e2.failures;
            } else {
                // TODO: Change this to something like "CouldNotParse"
                parseFailures = List.of("MessageMustBeArrayWithTwoElements");
            }

            var requestHeaders = new HashMap<String, Object>();
            requestHeaders.put("_parseFailures", parseFailures);

            return new Message(requestHeaders, Map.of());
        }

        return requestMessage;
    }

    static Message processMessage(Message requestMessage,
            JApiSchemaTuple jApiSchema,
            Function<Message, Message> handler,
            Consumer<Throwable> onError) {
        boolean unsafeResponseEnabled = false;
        var responseHeaders = (Map<String, Object>) new HashMap<String, Object>();
        var requestHeaders = requestMessage.header;
        var requestBody = requestMessage.body;
        var requestPayload = (Map<String, Object>) requestBody.values().stream().findAny().orElse(Map.of());
        var requestTarget = (String) requestBody.keySet().stream().findAny().orElse("fn._unknown");
        var unknownTarget = (String) null;
        if (!jApiSchema.parsed.containsKey(requestTarget)) {
            unknownTarget = requestTarget;
            requestTarget = "fn._unknown";
        }
        var functionType = (Fn) jApiSchema.parsed.get(requestTarget);
        var resultEnumType = functionType.result;
        var argStructType = (Struct) functionType.arg;

        // Reflect call id
        var callId = requestHeaders.get("_id");
        if (callId != null) {
            responseHeaders.put("_id", callId);
        }

        if (requestHeaders.containsKey("_parseFailures")) {
            var parseFailures = (List<String>) requestHeaders.get("_parseFailures");
            Map<String, Object> newErrorResult = Map.of("_errorParseFailure",
                    Map.of("reasons", parseFailures));
            var newErrorResultValidationFailures = InternalValidate.validateResultEnum(resultEnumType,
                    newErrorResult);
            if (!newErrorResultValidationFailures.isEmpty()) {
                throw new JApiProcessError("Failed internal jAPI validation");
            }
            return new Message(responseHeaders, newErrorResult);
        }

        var headerValidationFailures = InternalValidate.validateHeaders(requestHeaders, jApiSchema, functionType);

        if (!headerValidationFailures.isEmpty()) {
            var validationFailureCases = mapValidationFailuresToInvalidFieldCases(headerValidationFailures);
            Map<String, Object> newErrorResult = Map.of("_errorInvalidRequestHeaders",
                    Map.of("cases", validationFailureCases));
            var newErrorResultValidationFailures = InternalValidate.validateResultEnum(resultEnumType,
                    newErrorResult);
            if (!newErrorResultValidationFailures.isEmpty()) {
                throw new JApiProcessError("Failed internal jAPI validation");
            }
            return new Message(responseHeaders, newErrorResult);
        }

        if (requestHeaders.containsKey("_bin")) {
            List<Object> clientKnownBinaryChecksums = (List<Object>) requestHeaders.get("_bin");
            responseHeaders.put("_serializeAsBinary", true);
            responseHeaders.put("_clientKnownBinaryChecksums", clientKnownBinaryChecksums);
        }

        if (unknownTarget != null) {
            Map<String, Object> newErrorResult = Map.of("_errorInvalidRequestBody",
                    Map.of("cases", List.of(Map.of("path", unknownTarget, "reason", "UnknownFunction"))));
            var newErrorResultValidationFailures = InternalValidate.validateResultEnum(resultEnumType,
                    newErrorResult);
            if (!newErrorResultValidationFailures.isEmpty()) {
                throw new JApiProcessError("Failed internal jAPI validation");
            }
            return new Message(responseHeaders, newErrorResult);
        }

        var argumentValidationFailures = InternalValidate.validateStructFields(functionType.name,
                argStructType.fields, requestPayload);
        if (!argumentValidationFailures.isEmpty()) {
            var validationFailureCases = mapValidationFailuresToInvalidFieldCases(argumentValidationFailures);
            Map<String, Object> newErrorResult = Map.of("_errorInvalidRequestBody",
                    Map.of("cases", validationFailureCases));
            var newErrorResultValidationFailures = InternalValidate.validateResultEnum(resultEnumType,
                    newErrorResult);
            if (!newErrorResultValidationFailures.isEmpty()) {
                throw new JApiProcessError("Failed internal jAPI validation");
            }

            return new Message(responseHeaders, newErrorResult);
        }

        unsafeResponseEnabled = Objects.equals(true, requestHeaders.get("_unsafe"));

        var callMessage = new Message(requestHeaders, requestTarget, requestPayload);

        Message resultMessage;
        if (requestTarget.equals("fn._ping")) {
            resultMessage = new Message("ok", Map.of());
        } else if (requestTarget.equals("fn._api")) {
            resultMessage = new Message("ok", Map.of("api", jApiSchema.original));
        } else {
            try {
                resultMessage = handler.apply(callMessage);
            } catch (Throwable t) {
                try {
                    onError.accept(t);
                } catch (Throwable ignored) {

                }
                resultMessage = new Message("_errorUnknown", Map.of());
            }
        }
        var skipResultValidation = unsafeResponseEnabled;
        if (!skipResultValidation) {
            var resultValidationFailures = InternalValidate.validateResultEnum(
                    resultEnumType,
                    resultMessage.body);
            if (!resultValidationFailures.isEmpty()) {
                var validationFailureCases = mapValidationFailuresToInvalidFieldCases(resultValidationFailures);
                Map<String, Object> newErrorResult = Map.of("_errorInvalidResponseBody",
                        Map.of("cases", validationFailureCases));
                var newErrorResultValidationFailures = InternalValidate.validateResultEnum(resultEnumType,
                        newErrorResult);
                if (!newErrorResultValidationFailures.isEmpty()) {
                    throw new JApiProcessError("Failed internal jAPI validation");
                }
                return new Message(responseHeaders, newErrorResult);
            }
        }

        Map<String, Object> resultEnum = resultMessage.body;
        resultMessage.header.putAll(responseHeaders);
        responseHeaders = resultMessage.header;

        Map<String, Object> finalResultEnum;
        if (requestHeaders.containsKey("_sel")) {
            Map<String, List<String>> selectStructFieldsHeader = (Map<String, List<String>>) requestHeaders
                    .get("_sel");
            finalResultEnum = (Map<String, Object>) selectStructFields(resultEnumType, resultEnum,
                    selectStructFieldsHeader);
        } else {
            finalResultEnum = resultEnum;
        }

        return new Message(responseHeaders, finalResultEnum);
    }

    private static List<Map<String, String>> mapValidationFailuresToInvalidFieldCases(
            List<ValidationFailure> argumentValidationFailures) {
        var validationFailureCases = new ArrayList<Map<String, String>>();
        for (var validationFailure : argumentValidationFailures) {
            var validationFailureCase = Map.of(
                    "path", validationFailure.path,
                    "reason", validationFailure.reason);
            validationFailureCases.add(validationFailureCase);
        }
        return validationFailureCases;
    }

    static Object selectStructFields(Type type, Object value, Map<String, List<String>> selectedStructFields) {
        if (type instanceof Struct s) {
            var selectedFields = selectedStructFields.get(s.name);
            var valueAsMap = (Map<String, Object>) value;
            var finalMap = new HashMap<>();
            for (var entry : valueAsMap.entrySet()) {
                var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    var field = s.fields.get(fieldName);
                    var valueWithSelectedFields = selectStructFields(field.typeDeclaration.type, entry.getValue(),
                            selectedStructFields);
                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }
            return finalMap;
        } else if (type instanceof Fn f) {
            var selectedFields = selectedStructFields.get(f.name);
            var valueAsMap = (Map<String, Object>) value;
            var finalMap = new HashMap<>();
            for (var entry : valueAsMap.entrySet()) {
                var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    var field = f.arg.fields.get(fieldName);
                    var valueWithSelectedFields = selectStructFields(field.typeDeclaration.type, entry.getValue(),
                            selectedStructFields);
                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }
            return finalMap;
        } else if (type instanceof Enum e) {
            return selectStructFieldsForEnum(e.values, value, selectedStructFields);
        } else if (type instanceof JsonObject o) {
            var valueAsMap = (Map<String, Object>) value;
            var finalMap = new HashMap<>();
            for (var entry : valueAsMap.entrySet()) {
                var valueWithSelectedFields = selectStructFields(o.nestedType.type, entry.getValue(),
                        selectedStructFields);
                finalMap.put(entry.getKey(), valueWithSelectedFields);
            }
            return finalMap;
        } else if (type instanceof JsonArray a) {
            var valueAsList = (List<Object>) value;
            var finalList = new ArrayList<>();
            for (var entry : valueAsList) {
                var valueWithSelectedFields = selectStructFields(a.nestedType.type, entry, selectedStructFields);
                finalList.add(valueWithSelectedFields);
            }
            return finalList;
        } else {
            return value;
        }
    }

    static Object selectStructFieldsForEnum(Map<String, Struct> enumReference, Object value,
            Map<String, List<String>> selectedStructFields) {
        var valueAsMap = (Map<String, Object>) value;
        var enumEntry = valueAsMap.entrySet().stream().findFirst().get();
        var enumValue = enumEntry.getKey();
        var enumData = enumEntry.getValue();

        var enumStructReference = enumReference.get(enumValue);
        var structWithSelectedFields = selectStructFields(enumStructReference, enumData, selectedStructFields);
        return Map.of(enumEntry.getKey(), structWithSelectedFields);
    }
}
