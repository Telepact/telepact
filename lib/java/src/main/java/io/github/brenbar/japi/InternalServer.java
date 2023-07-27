package io.github.brenbar.japi;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.BiFunction;
import java.util.regex.Pattern;

class InternalServer {

    static Message parseRequestMessage(byte[] requestMessageBytes, Serializer serializer, JApiSchema jApiSchema) {
        var requestTarget = "fn._unknown";
        var requestHeaders = new HashMap<String, Object>();
        var parseFailures = new ArrayList<String>();

        List<Object> requestMessageArray;
        try {
            requestMessageArray = serializer.deserialize(requestMessageBytes);
        } catch (DeserializationError e) {
            var cause = e.getCause();

            if (cause instanceof BinaryEncoderUnavailableError e2) {
                parseFailures.add("BinaryDecodeFailure");
            } else if (cause instanceof BinaryEncoderMissingEncoding e2) {
                parseFailures.add("BinaryDecodeFailure");
            } else {
                parseFailures.add("MessageMustBeArrayWithThreeElements");
            }

            if (!parseFailures.isEmpty()) {
                requestHeaders.put("_parseFailures", parseFailures);
            }

            return new Message(requestTarget, requestHeaders, Map.of());
        }

        Map<String, Object> body = new HashMap<>();
        if (requestMessageArray.size() != 3) {
            parseFailures.add("MessageMustBeArrayWithThreeElements");
        } else {
            try {
                var givenTarget = (String) requestMessageArray.get(0);

                var regex = Pattern.compile("^fn\\.([a-zA-Z_]\\w*)");
                var matcher = regex.matcher(givenTarget);
                if (matcher.matches()) {
                    var functionDef = jApiSchema.parsed.get(givenTarget);
                    if (functionDef instanceof FunctionDefinition f) {
                        requestTarget = givenTarget;
                    } else {
                        parseFailures.add("UnknownFunction");
                    }
                } else {
                    parseFailures.add("TargetStringMustBeFunction");
                }

            } catch (ClassCastException e) {
                parseFailures.add("TargetMustBeString");
            }

            try {
                var headers = (Map<String, Object>) requestMessageArray.get(1);
                requestHeaders.putAll(headers);
            } catch (ClassCastException e) {
                parseFailures.add("HeadersMustBeObject");
            }

            try {
                body = (Map<String, Object>) requestMessageArray.get(2);
            } catch (ClassCastException e) {
                parseFailures.add("BodyMustBeObject");
            }
        }

        if (!parseFailures.isEmpty()) {
            requestHeaders.put("_parseFailures", parseFailures);
        }

        return new Message(requestTarget, requestHeaders, body);
    }

    static Message processMessage(Message requestMessage,
            JApiSchema jApiSchema,
            BiFunction<Context, Map<String, Object>, Map<String, Object>> handler) {
        var responseMessage = processMessageWithoutResultValidation(requestMessage, jApiSchema, handler);

        return responseMessage;
    }

    static Message processMessageWithoutResultValidation(Message requestMessage,
            JApiSchema jApiSchema,
            BiFunction<Context, Map<String, Object>, Map<String, Object>> handler) {
        boolean unsafeResponseEnabled = false;
        var responseHeaders = new HashMap<String, Object>();
        var requestTarget = (String) requestMessage.target;
        var functionDefinition = (FunctionDefinition) jApiSchema.parsed.get(requestTarget);
        var requestHeaders = (Map<String, Object>) requestMessage.headers;
        var requestBody = (Map<String, Object>) requestMessage.body;

        // Reflect call id
        var callId = requestHeaders.get("_id");
        if (callId != null) {
            responseHeaders.put("_id", callId);
        }

        if (requestHeaders.containsKey("_parseFailures")) {
            var parseFailures = (List<String>) requestHeaders.get("_parseFailures");
            Map<String, Object> newErrorResult = Map.of("err",
                    Map.of("_parseFailure", Map.of("reasons", parseFailures)));
            var newErrorResultValidationFailures = validateResultEnum(requestTarget, functionDefinition,
                    newErrorResult);
            if (!newErrorResultValidationFailures.isEmpty()) {
                throw new JApiProcessError("Failed internal jAPI validation");
            }
            return new Message(requestTarget, responseHeaders, newErrorResult);
        }

        var headerValidationFailures = validateHeaders(requestHeaders, jApiSchema);

        if (!headerValidationFailures.isEmpty()) {
            var validationFailureCases = mapValidationFailuresToInvalidFieldCases(headerValidationFailures);
            Map<String, Object> newErrorResult = Map.of("err",
                    Map.of("_invalidRequestHeaders", Map.of("cases", validationFailureCases)));
            var newErrorResultValidationFailures = validateResultEnum(requestTarget, functionDefinition,
                    newErrorResult);
            if (!newErrorResultValidationFailures.isEmpty()) {
                throw new JApiProcessError("Failed internal jAPI validation");
            }
            return new Message(requestTarget, responseHeaders, newErrorResult);
        }

        if (requestHeaders.containsKey("_bin")) {
            List<Object> clientKnownBinaryChecksums = (List<Object>) requestHeaders.get("_bin");
            responseHeaders.put("_serializeAsBinary", true);
            responseHeaders.put("_clientKnownBinaryChecksums", clientKnownBinaryChecksums);
        }

        var inputValidationFailures = validateStruct(functionDefinition.name,
                functionDefinition.inputStruct.fields, requestBody);
        if (!inputValidationFailures.isEmpty()) {
            var validationFailureCases = mapValidationFailuresToInvalidFieldCases(inputValidationFailures);
            Map<String, Object> newErrorResult = Map.of("err",
                    Map.of("_invalidRequestBody", Map.of("cases", validationFailureCases)));
            var newErrorResultValidationFailures = validateResultEnum(requestTarget, functionDefinition,
                    newErrorResult);
            if (!newErrorResultValidationFailures.isEmpty()) {
                throw new JApiProcessError("Failed internal jAPI validation");
            }
            return new Message(requestTarget, responseHeaders, newErrorResult);
        }

        var context = new Context(requestTarget, requestHeaders);

        unsafeResponseEnabled = Objects.equals(true, requestHeaders.get("_unsafe"));

        Map<String, Object> result;
        if (requestTarget.equals("fn._ping")) {
            result = Map.of("ok", Map.of());
        } else if (requestTarget.equals("fn._jApi")) {
            result = Map.of("ok", Map.of("jApi", jApiSchema.original));
        } else {
            result = handler.apply(context, requestBody);
        }

        var resultValidationFailures = validateResultEnum(functionDefinition.name,
                functionDefinition,
                result);
        if (!resultValidationFailures.isEmpty() && !unsafeResponseEnabled) {
            var validationFailureCases = mapValidationFailuresToInvalidFieldCases(resultValidationFailures);
            Map<String, Object> newErrorResult = Map.of("err",
                    Map.of("_invalidResponseBody", Map.of("cases", validationFailureCases)));
            var newErrorResultValidationFailures = validateResultEnum(functionDefinition.name, functionDefinition,
                    newErrorResult);
            if (!newErrorResultValidationFailures.isEmpty()) {
                throw new JApiProcessError("Failed internal jAPI validation");
            }
            return new Message(requestTarget, responseHeaders, newErrorResult);
        }

        Map<String, Object> finalResult;
        if (requestHeaders.containsKey("_sel")) {
            Map<String, List<String>> selectStructFieldsHeader = (Map<String, List<String>>) requestHeaders
                    .get("_sel");
            finalResult = (Map<String, Object>) selectStructFields(functionDefinition.resultEnum, result,
                    selectStructFieldsHeader);
        } else {
            finalResult = result;
        }

        return new Message(requestTarget, responseHeaders, finalResult);
    }

    private static List<Map<String, String>> mapValidationFailuresToInvalidFieldCases(
            List<ValidationFailure> inputValidationFailures) {
        var validationFailureCases = new ArrayList<Map<String, String>>();
        for (var validationFailure : inputValidationFailures) {
            var validationFailureCase = Map.of(
                    "path", validationFailure.path,
                    "reason", validationFailure.reason);
            validationFailureCases.add(validationFailureCase);
        }
        return validationFailureCases;
    }

    private static List<ValidationFailure> validateHeaders(
            Map<String, Object> headers, JApiSchema jApiSchema) {
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
                if (!structName.startsWith("struct.")) {
                    validationFailures.add(new ValidationFailure("headers{_sel}{%s}".formatted(structName),
                            "SelectHeaderKeyMustBeStructReference"));
                    continue;
                }
                var structReference = jApiSchema.parsed.get(structName);
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
                    if (structReference instanceof TypeDefinition d) {
                        if (d.type instanceof Struct s) {
                            if (!s.fields.containsKey(stringField)) {
                                validationFailures.add(new ValidationFailure(
                                        "headers{_sel}{%s}[%d]".formatted(structName, i),
                                        "UnknownStructField"));
                            }
                        }
                    }
                }
            }

        }

        return validationFailures;
    }

    private static List<ValidationFailure> validateResultEnum(
            String path,
            FunctionDefinition functionDefinition,
            Map<String, Object> actualResult) {
        return validateEnum(path, functionDefinition.resultEnum.values, actualResult);
    }

    private static List<ValidationFailure> validateStruct(
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

    private static List<ValidationFailure> validateEnum(
            String path,
            Map<String, Object> referenceValues,
            Map<?, ?> actual) {
        if (actual.size() != 1) {
            return Collections.singletonList(
                    new ValidationFailure(path,
                            ValidationErrorReasons.MULTI_ENTRY_OBJECT_INVALID_FOR_ENUM_TYPE));
        }
        var entry = actual.entrySet().stream().findFirst().get();
        var enumValue = (String) entry.getKey();
        var enumData = entry.getValue();

        if (enumData instanceof Boolean) {
            return Collections.singletonList(new ValidationFailure(path,
                    ValidationErrorReasons.BOOLEAN_INVALID_FOR_ENUM_STRUCT_TYPE));
        } else if (enumData instanceof Number) {
            return Collections.singletonList(new ValidationFailure(path,
                    ValidationErrorReasons.NUMBER_INVALID_FOR_ENUM_STRUCT_TYPE));
        } else if (enumData instanceof String) {
            return Collections.singletonList(new ValidationFailure(path,
                    ValidationErrorReasons.STRING_INVALID_FOR_ENUM_STRUCT_TYPE));
        } else if (enumData instanceof List) {
            return Collections.singletonList(new ValidationFailure(path,
                    ValidationErrorReasons.ARRAY_INVALID_FOR_ENUM_STRUCT_TYPE));
        } else if (enumData instanceof Map<?, ?> m2) {
            return validateEnumData("%s.%s".formatted(path, enumValue), referenceValues, enumValue,
                    (Map<String, Object>) m2);
        } else {
            return Collections.singletonList(new ValidationFailure(path,
                    ValidationErrorReasons.VALUE_INVALID_FOR_ENUM_STRUCT_TYPE));
        }
    }

    private static List<ValidationFailure> validateEnumData(
            String path,
            Map<String, Object> reference,
            String enumCase,
            Map<String, Object> actual) {
        var validationFailures = new ArrayList<ValidationFailure>();

        var referenceField = reference.get(enumCase);
        if (referenceField == null) {
            return Collections
                    .singletonList(new ValidationFailure(path,
                            ValidationErrorReasons.UNKNOWN_ENUM_VALUE));
        } else if (referenceField instanceof Struct s) {

            var nestedValidationFailures = validateStruct(path, s.fields,
                    actual);
            validationFailures.addAll(nestedValidationFailures);

            return validationFailures;
        } else if (referenceField instanceof Map<?, ?> m) {
            return validateEnum(path, (Map<String, Object>) m, actual);
        } else {
            throw new JApiProcessError("Unexpected enum reference type");
        }
    }

    private static List<ValidationFailure> validateType(String fieldName, TypeDeclaration typeDeclaration,
            Object value) {
        if (value == null) {
            if (!typeDeclaration.nullable) {
                return Collections.singletonList(new ValidationFailure(fieldName,
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
                            new ValidationFailure(fieldName, ValidationErrorReasons.NUMBER_INVALID_FOR_BOOLEAN_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.STRING_INVALID_FOR_BOOLEAN_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.ARRAY_INVALID_FOR_BOOLEAN_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.OBJECT_INVALID_FOR_BOOLEAN_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.VALUE_INVALID_FOR_BOOLEAN_TYPE));
                }
            } else if (expectedType instanceof JsonInteger) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.BOOLEAN_INVALID_FOR_INTEGER_TYPE));
                } else if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.NUMBER_OUT_OF_RANGE));
                } else if (value instanceof Number) {
                    if (value instanceof Long || value instanceof Integer) {
                        return Collections.emptyList();
                    } else {
                        return Collections.singletonList(new ValidationFailure(fieldName,
                                ValidationErrorReasons.NUMBER_INVALID_FOR_INTEGER_TYPE));
                    }
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.STRING_INVALID_FOR_INTEGER_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.ARRAY_INVALID_FOR_INTEGER_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.OBJECT_INVALID_FOR_INTEGER_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.VALUE_INVALID_FOR_INTEGER_TYPE));
                }
            } else if (expectedType instanceof JsonNumber) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.BOOLEAN_INVALID_FOR_NUMBER_TYPE));
                } else if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.NUMBER_OUT_OF_RANGE));
                } else if (value instanceof Number) {
                    return Collections.emptyList();
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.STRING_INVALID_FOR_NUMBER_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.ARRAY_INVALID_FOR_NUMBER_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.OBJECT_INVALID_FOR_NUMBER_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.OBJECT_INVALID_FOR_NUMBER_TYPE));
                }
            } else if (expectedType instanceof JsonString) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.BOOLEAN_INVALID_FOR_STRING_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.NUMBER_INVALID_FOR_STRING_TYPE));
                } else if (value instanceof String) {
                    return Collections.emptyList();
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.ARRAY_INVALID_FOR_STRING_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.OBJECT_INVALID_FOR_STRING_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.VALUE_INVALID_FOR_STRING_TYPE));
                }
            } else if (expectedType instanceof JsonArray a) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.BOOLEAN_INVALID_FOR_ARRAY_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.NUMBER_INVALID_FOR_ARRAY_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.STRING_INVALID_FOR_ARRAY_TYPE));
                } else if (value instanceof List l) {
                    var validationFailures = new ArrayList<ValidationFailure>();
                    for (var i = 0; i < l.size(); i += 1) {
                        var element = l.get(i);
                        var nestedValidationFailures = validateType("%s[%s]".formatted(fieldName, i), a.nestedType,
                                element);
                        validationFailures.addAll(nestedValidationFailures);
                    }
                    return validationFailures;
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.OBJECT_INVALID_FOR_ARRAY_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.VALUE_INVALID_FOR_ARRAY_TYPE));
                }
            } else if (expectedType instanceof JsonObject o) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.BOOLEAN_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.NUMBER_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.STRING_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.ARRAY_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof Map<?, ?> m) {
                    var validationFailures = new ArrayList<ValidationFailure>();
                    for (Map.Entry<?, ?> entry : m.entrySet()) {
                        var k = (String) entry.getKey();
                        var v = entry.getValue();
                        var nestedValidationFailures = validateType("%s{%s}".formatted(fieldName, k), o.nestedType,
                                v);
                        validationFailures.addAll(nestedValidationFailures);
                    }
                    return validationFailures;
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.VALUE_INVALID_FOR_OBJECT_TYPE));
                }
            } else if (expectedType instanceof Struct s) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.BOOLEAN_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.NUMBER_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.STRING_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.ARRAY_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof Map<?, ?> m) {
                    return validateStruct(fieldName, s.fields, (Map<String, Object>) m);
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.VALUE_INVALID_FOR_STRUCT_TYPE));
                }
            } else if (expectedType instanceof Enum e) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.BOOLEAN_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.NUMBER_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.STRING_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.ARRAY_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof Map<?, ?> m) {
                    return validateEnum(fieldName, e.values, m);
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrorReasons.VALUE_INVALID_FOR_ENUM_TYPE));
                }
            } else if (expectedType instanceof JsonAny a) {
                // all values are valid for any
                return Collections.emptyList();
            } else {
                return Collections.singletonList(new ValidationFailure(fieldName, ValidationErrorReasons.INVALID_TYPE));
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

    static Object selectStructFieldsForEnum(Map<String, Object> enumReference, Object value,
            Map<String, List<String>> selectedStructFields) {
        var valueAsMap = (Map<String, Object>) value;
        var enumEntry = valueAsMap.entrySet().stream().findFirst().get();
        var enumValue = enumEntry.getKey();
        var enumData = enumEntry.getValue();

        var enumEntryReference = enumReference.get(enumValue);
        if (enumEntryReference instanceof Struct structReference) {
            var structWithSelectedFields = selectStructFields(structReference, enumData, selectedStructFields);
            return Map.of(enumEntry.getKey(), structWithSelectedFields);
        } else if (enumEntryReference instanceof Map<?, ?> m) {
            var subSelect = selectStructFieldsForEnum((Map<String, Object>) m, enumData, selectedStructFields);
            return Map.of(enumValue, subSelect);
        } else {
            throw new JApiProcessError("Unexpected enum reference type");
        }
    }
}
