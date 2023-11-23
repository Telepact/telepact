package io.github.brenbar.japi;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Function;

class InternalServer {

    static Message parseRequestMessage(byte[] requestMessageBytes, Serializer serializer, JApiSchema jApiSchema,
            Consumer<Throwable> onError) {
        var requestHeaders = new HashMap<String, Object>();
        var parseFailures = new ArrayList<String>();

        Message requestMessage;
        try {
            requestMessage = serializer.deserialize(requestMessageBytes);
        } catch (DeserializationError e) {
            try {
                onError.accept(e);
            } catch (Throwable ignored) {
            }
            var cause = e.getCause();

            if (cause instanceof BinaryEncoderUnavailableError e2) {
                parseFailures.add("IncompatibleBinaryEncoding");
            } else if (cause instanceof BinaryEncodingMissing e2) {
                parseFailures.add("BinaryDecodeFailure");
            } else if (cause instanceof InvalidJsonError e2) {
                parseFailures.add("InvalidJson");
            } else if (cause instanceof MessageParseError e2) {
                parseFailures.addAll(e2.failures);
            } else {
                // TODO: Change this to something like "CouldNotParse"
                parseFailures.add("MessageMustBeArrayWithTwoElements");
            }

            if (!parseFailures.isEmpty()) {
                requestHeaders.put("_parseFailures", parseFailures);
            }

            return new Message(requestHeaders, Map.of());
        }

        if (!parseFailures.isEmpty()) {
            requestHeaders.put("_parseFailures", parseFailures);
        }

        requestMessage.header.putAll(requestHeaders);

        return requestMessage;
    }

    static Message processMessage(Message requestMessage,
            JApiSchema jApiSchema,
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

        Map<String, Object> features = null;
        if (requestHeaders.containsKey("_features")) {
            try {
                features = (Map<String, Object>) requestHeaders.get("_features");
            } catch (ClassCastException e) {
                throw new JApiProcessError("Invalid header. Path: headers{_features}");
            }
        }

        boolean featureIgnoreMissingArgStructFields = false;
        if (features != null) {
            try {
                featureIgnoreMissingArgStructFields = (Boolean) features.get("ignoreMissingStructFields");
            } catch (ClassCastException | NullPointerException e) {
                throw new JApiProcessError("Invalid header. Path: headers{_features}{ignoreMissingStructFields}");
            }
        }

        if (requestHeaders.containsKey("_parseFailures")) {
            var parseFailures = (List<String>) requestHeaders.get("_parseFailures");
            Map<String, Object> newErrorResult = Map.of("_errorParseFailure",
                    Map.of("reasons", parseFailures));
            var newErrorResultValidationFailures = validateResultEnum(resultEnumType,
                    newErrorResult);
            if (!newErrorResultValidationFailures.isEmpty()) {
                throw new JApiProcessError("Failed internal jAPI validation");
            }
            return new Message(responseHeaders, newErrorResult);
        }

        var headerValidationFailures = validateHeaders(requestHeaders, jApiSchema, functionType);

        if (!headerValidationFailures.isEmpty()) {
            var validationFailureCases = mapValidationFailuresToInvalidFieldCases(headerValidationFailures);
            Map<String, Object> newErrorResult = Map.of("_errorInvalidRequestHeaders",
                    Map.of("cases", validationFailureCases));
            var newErrorResultValidationFailures = validateResultEnum(resultEnumType,
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
            Map<String, Object> newErrorResult = Map.of("_errorParseFailure",
                    Map.of("reasons", List.of("UnknownFunction")));
            var newErrorResultValidationFailures = validateResultEnum(resultEnumType,
                    newErrorResult);
            if (!newErrorResultValidationFailures.isEmpty()) {
                throw new JApiProcessError("Failed internal jAPI validation");
            }
            return new Message(responseHeaders, newErrorResult);
        }

        var argumentValidationFailures = validateStruct(functionType.name,
                argStructType.fields, requestPayload);
        if (!argumentValidationFailures.isEmpty()) {
            var allErrorsAreMissingStructFields = argumentValidationFailures.stream()
                    .allMatch(e -> e.reason.equals(ValidationErrorReasons.REQUIRED_STRUCT_FIELD_MISSING));

            // TODO: Complete this feature
            // var shouldValidate = !shouldValidateArgument.apply(context, requestBody) ||
            // !allErrorsAreMissingStructFields;

            var validationFailureCases = mapValidationFailuresToInvalidFieldCases(argumentValidationFailures);
            Map<String, Object> newErrorResult = Map.of("_errorInvalidRequestBody",
                    Map.of("cases", validationFailureCases));
            var newErrorResultValidationFailures = validateResultEnum(resultEnumType,
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
        } else if (requestTarget.equals("fn._jApi")) {
            resultMessage = new Message("ok", Map.of("jApi", jApiSchema.original));
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
            var resultValidationFailures = validateResultEnum(
                    resultEnumType,
                    resultMessage.body);
            if (!resultValidationFailures.isEmpty()) {
                var validationFailureCases = mapValidationFailuresToInvalidFieldCases(resultValidationFailures);
                Map<String, Object> newErrorResult = Map.of("_errorInvalidResponseBody",
                        Map.of("cases", validationFailureCases));
                var newErrorResultValidationFailures = validateResultEnum(resultEnumType,
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

    private static List<ValidationFailure> validateHeaders(
            Map<String, Object> headers, JApiSchema jApiSchema, Fn functionType) {
        var validationFailures = new ArrayList<ValidationFailure>();

        if (headers.containsKey("_bin")) {
            List<Object> binaryChecksums;
            try {
                binaryChecksums = (List<Object>) headers.get("_bin");
                for (var binaryChecksum : binaryChecksums) {
                    try {
                        var integerElement = (Integer) binaryChecksum;
                    } catch (ClassCastException e) {
                        var longElement = (Long) binaryChecksum;
                    }
                }
            } catch (ClassCastException e) {
                validationFailures.add(new ValidationFailure("headers{_bin}", "BinaryHeaderMustBeArrayOfIntegers"));
            }
        }

        if (headers.containsKey("_sel")) {
            Map<String, Object> selectStructFieldsHeader = new HashMap<>();
            try {
                selectStructFieldsHeader = (Map<String, Object>) headers
                        .get("_sel");

            } catch (ClassCastException e) {
                validationFailures.add(new ValidationFailure("headers{_sel}",
                        "SelectHeaderMustBeObject"));
            }
            for (Map.Entry<String, Object> entry : selectStructFieldsHeader.entrySet()) {
                var structName = entry.getKey();
                if (!structName.startsWith("struct.") && !structName.startsWith("->.")
                        && !structName.startsWith("fn.")) {
                    validationFailures.add(new ValidationFailure("headers{_sel}{%s}".formatted(structName),
                            "SelectHeaderKeyMustBeStructReference"));
                    continue;
                }

                Struct structReference;
                if (structName.startsWith("->.")) {
                    var resultEnumValue = structName.split("->.")[1];
                    structReference = functionType.result.values.get(resultEnumValue);
                } else if (structName.startsWith("fn.")) {
                    var functionRef = (Fn) jApiSchema.parsed.get(structName);
                    structReference = functionRef.arg;
                } else {
                    structReference = (Struct) jApiSchema.parsed.get(structName);
                }

                if (structReference == null) {
                    validationFailures.add(new ValidationFailure("headers{_sel}{%s}".formatted(structName),
                            "UnknownStruct"));
                    continue;
                }

                List<Object> fields = new ArrayList<>();
                try {
                    fields = (List<Object>) entry.getValue();
                } catch (ClassCastException e) {
                    validationFailures.add(new ValidationFailure("headers{_sel}{%s}".formatted(structName),
                            "SelectHeaderFieldsMustBeArray"));
                }

                for (int i = 0; i < fields.size(); i += 1) {
                    var field = fields.get(i);
                    String stringField;
                    try {
                        stringField = (String) field;
                    } catch (ClassCastException e) {
                        validationFailures.add(new ValidationFailure(
                                "headers{_sel}{%s}[%d]".formatted(structName, i),
                                "SelectHeaderFieldMustBeString"));
                        continue;
                    }
                    if (!structReference.fields.containsKey(stringField)) {
                        validationFailures.add(new ValidationFailure(
                                "headers{_sel}{%s}[%d]".formatted(structName, i),
                                "UnknownStructField"));
                    }
                }
            }

        }

        return validationFailures;

    }

    private static List<ValidationFailure> validateResultEnum(
            Enum resultEnumType,
            Map<String, Object> actualResult) {
        return validateEnum("", resultEnumType.values, actualResult);
    }

    static List<ValidationFailure> validateStruct(
            String path,
            Map<String, FieldDeclaration> referenceStruct,
            Map<String, Object> actualStruct) {
        var validationFailures = new ArrayList<ValidationFailure>();

        var missingFields = new ArrayList<String>();
        for (Map.Entry<String, FieldDeclaration> entry : referenceStruct.entrySet()) {
            var fieldName = entry.getKey();
            var fieldDeclaration = entry.getValue();
            if (!actualStruct.containsKey(fieldName) && !fieldDeclaration.optional) {
                missingFields.add(fieldName);
            }
        }

        for (var missingField : missingFields) {
            var validationFailure = new ValidationFailure("%s.%s".formatted(path, missingField),
                    ValidationErrorReasons.REQUIRED_STRUCT_FIELD_MISSING);
            validationFailures
                    .add(validationFailure);
        }

        for (Map.Entry<String, Object> entry : actualStruct.entrySet()) {
            var fieldName = entry.getKey();
            var field = entry.getValue();
            var referenceField = referenceStruct.get(fieldName);
            if (referenceField == null) {
                var validationFailure = new ValidationFailure("%s.%s".formatted(path, fieldName),
                        ValidationErrorReasons.EXTRA_STRUCT_FIELD_NOT_ALLOWED);
                validationFailures
                        .add(validationFailure);
                continue;
            }
            var nestedValidationFailures = validateType("%s.%s".formatted(path, fieldName),
                    referenceField.typeDeclaration, field);
            validationFailures.addAll(nestedValidationFailures);
        }

        return validationFailures;
    }

    static List<ValidationFailure> validateEnum(
            String path,
            Map<String, Struct> referenceValues,
            Map<?, ?> actual) {
        if (actual.size() != 1) {
            return Collections.singletonList(
                    new ValidationFailure(path,
                            ValidationErrorReasons.MULTI_ENTRY_OBJECT_INVALID_FOR_ENUM_TYPE));
        }
        var entry = actual.entrySet().stream().findFirst().get();
        var enumTarget = (String) entry.getKey();
        var enumPayload = entry.getValue();

        var nextPath = !"".equals(path) ? "%s.%s".formatted(path, enumTarget) : enumTarget;

        var referenceStruct = referenceValues.get(enumTarget);
        if (referenceStruct == null) {
            return Collections
                    .singletonList(new ValidationFailure(nextPath,
                            ValidationErrorReasons.UNKNOWN_ENUM_VALUE));
        }

        if (enumPayload instanceof Boolean) {
            return Collections.singletonList(new ValidationFailure(nextPath,
                    ValidationErrorReasons.BOOLEAN_INVALID_FOR_ENUM_STRUCT_TYPE));
        } else if (enumPayload instanceof Number) {
            return Collections.singletonList(new ValidationFailure(nextPath,
                    ValidationErrorReasons.NUMBER_INVALID_FOR_ENUM_STRUCT_TYPE));
        } else if (enumPayload instanceof String) {
            return Collections.singletonList(new ValidationFailure(nextPath,
                    ValidationErrorReasons.STRING_INVALID_FOR_ENUM_STRUCT_TYPE));
        } else if (enumPayload instanceof List) {
            return Collections.singletonList(new ValidationFailure(nextPath,
                    ValidationErrorReasons.ARRAY_INVALID_FOR_ENUM_STRUCT_TYPE));
        } else if (enumPayload instanceof Map<?, ?> m2) {
            return validateEnumStruct(nextPath, referenceStruct, enumTarget,
                    (Map<String, Object>) m2);
        } else {
            return Collections.singletonList(new ValidationFailure(nextPath,
                    ValidationErrorReasons.VALUE_INVALID_FOR_ENUM_STRUCT_TYPE));
        }
    }

    private static List<ValidationFailure> validateEnumStruct(
            String path,
            Struct enumStruct,
            String enumCase,
            Map<String, Object> actual) {
        var validationFailures = new ArrayList<ValidationFailure>();

        var nestedValidationFailures = validateStruct(path, enumStruct.fields,
                actual);
        validationFailures.addAll(nestedValidationFailures);

        return validationFailures;
    }

    private static List<ValidationFailure> validateType(String path, TypeDeclaration typeDeclaration,
            Object value) {
        if (value == null) {
            if (!typeDeclaration.nullable) {
                return Collections.singletonList(new ValidationFailure(path,
                        ValidationErrorReasons.NULL_INVALID_FOR_NON_NULL_TYPE));
            } else {
                return Collections.emptyList();
            }
        } else {
            var expectedType = typeDeclaration.type;
            if (expectedType instanceof JsonBoolean) {
                if (value instanceof Boolean) {
                    return Collections.emptyList();
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.NUMBER_INVALID_FOR_BOOLEAN_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.STRING_INVALID_FOR_BOOLEAN_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.ARRAY_INVALID_FOR_BOOLEAN_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.OBJECT_INVALID_FOR_BOOLEAN_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.VALUE_INVALID_FOR_BOOLEAN_TYPE));
                }
            } else if (expectedType instanceof JsonInteger) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.BOOLEAN_INVALID_FOR_INTEGER_TYPE));
                } else if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.NUMBER_OUT_OF_RANGE));
                } else if (value instanceof Number) {
                    if (value instanceof Long || value instanceof Integer) {
                        return Collections.emptyList();
                    } else {
                        return Collections.singletonList(new ValidationFailure(path,
                                ValidationErrorReasons.NUMBER_INVALID_FOR_INTEGER_TYPE));
                    }
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.STRING_INVALID_FOR_INTEGER_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.ARRAY_INVALID_FOR_INTEGER_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.OBJECT_INVALID_FOR_INTEGER_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.VALUE_INVALID_FOR_INTEGER_TYPE));
                }
            } else if (expectedType instanceof JsonNumber) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.BOOLEAN_INVALID_FOR_NUMBER_TYPE));
                } else if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.NUMBER_OUT_OF_RANGE));
                } else if (value instanceof Number) {
                    return Collections.emptyList();
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.STRING_INVALID_FOR_NUMBER_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.ARRAY_INVALID_FOR_NUMBER_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.OBJECT_INVALID_FOR_NUMBER_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.OBJECT_INVALID_FOR_NUMBER_TYPE));
                }
            } else if (expectedType instanceof JsonString) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.BOOLEAN_INVALID_FOR_STRING_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.NUMBER_INVALID_FOR_STRING_TYPE));
                } else if (value instanceof String) {
                    return Collections.emptyList();
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.ARRAY_INVALID_FOR_STRING_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.OBJECT_INVALID_FOR_STRING_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.VALUE_INVALID_FOR_STRING_TYPE));
                }
            } else if (expectedType instanceof JsonArray a) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.BOOLEAN_INVALID_FOR_ARRAY_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.NUMBER_INVALID_FOR_ARRAY_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.STRING_INVALID_FOR_ARRAY_TYPE));
                } else if (value instanceof List l) {
                    var validationFailures = new ArrayList<ValidationFailure>();
                    for (var i = 0; i < l.size(); i += 1) {
                        var element = l.get(i);
                        var nestedValidationFailures = validateType("%s[%s]".formatted(path, i), a.nestedType,
                                element);
                        validationFailures.addAll(nestedValidationFailures);
                    }
                    return validationFailures;
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.OBJECT_INVALID_FOR_ARRAY_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.VALUE_INVALID_FOR_ARRAY_TYPE));
                }
            } else if (expectedType instanceof JsonObject o) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.BOOLEAN_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.NUMBER_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.STRING_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.ARRAY_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof Map<?, ?> m) {
                    var validationFailures = new ArrayList<ValidationFailure>();
                    for (Map.Entry<?, ?> entry : m.entrySet()) {
                        var k = (String) entry.getKey();
                        var v = entry.getValue();
                        var nestedValidationFailures = validateType("%s{%s}".formatted(path, k), o.nestedType,
                                v);
                        validationFailures.addAll(nestedValidationFailures);
                    }
                    return validationFailures;
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.VALUE_INVALID_FOR_OBJECT_TYPE));
                }
            } else if (expectedType instanceof Struct s) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.BOOLEAN_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.NUMBER_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.STRING_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.ARRAY_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof Map<?, ?> m) {
                    return validateStruct(path, s.fields, (Map<String, Object>) m);
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.VALUE_INVALID_FOR_STRUCT_TYPE));
                }
            } else if (expectedType instanceof Enum e) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.BOOLEAN_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.NUMBER_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.STRING_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.ARRAY_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof Map<?, ?> m) {
                    return validateEnum(path, e.values, m);
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(path, ValidationErrorReasons.VALUE_INVALID_FOR_ENUM_TYPE));
                }
            } else if (expectedType instanceof Fn f) {
                return validateType(path, new TypeDeclaration(f.arg, false), value);
            } else if (expectedType instanceof Ext e) {
                return e.typeExtension.validate(path, value);
            } else if (expectedType instanceof JsonAny a) {
                // all values are valid for any
                return Collections.emptyList();
            } else {
                return Collections.singletonList(new ValidationFailure(path, ValidationErrorReasons.INVALID_TYPE));
            }
        }
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
