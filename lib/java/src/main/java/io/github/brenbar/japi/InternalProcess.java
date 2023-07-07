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
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.regex.Pattern;

class InternalProcess {

    static List<Object> processObject(List<Object> inputMessage, Consumer<Throwable> onError,
            BinaryEncoder binaryEncoder,
            Map<String, Definition> jApi,
            Map<String, Object> originalJApiAsParsedJson,
            BiFunction<Context, Map<String, Object>, Map<String, Object>> handler,
            Function<Map<String, Object>, Map<String, Object>> extractContextProperties) {

        var outputHeaders = new HashMap<String, Object>();
        try {
            try {
                if (inputMessage.size() < 3) {
                    throw new JApiError("error._ParseFailure", Map.of("reason", "MessageMustBeArrayWithThreeElements"));
                }

                String inputTarget;
                try {
                    inputTarget = (String) inputMessage.get(0);
                } catch (ClassCastException e) {
                    throw new JApiError("error._ParseFailure", Map.of("reason", "TargetMustBeString"));
                }

                var regex = Pattern.compile("^function\\.([a-zA-Z_]\\w*)");
                var matcher = regex.matcher(inputTarget);
                if (!matcher.matches()) {
                    throw new JApiError("error._ParseFailure",
                            Map.of("reason", "TargetStringMustBeFunction"));
                }
                var functionName = matcher.group(1);

                Map<String, Object> inputHeaders;
                try {
                    inputHeaders = (Map<String, Object>) inputMessage.get(1);
                } catch (ClassCastException e) {
                    throw new JApiError("error._ParseFailure", Map.of("reason", "HeadersMustBeObject"));
                }

                var headerValidationFailures = validateHeaders(inputHeaders, jApi);

                if (!headerValidationFailures.isEmpty()) {
                    var validationFailureCases = new ArrayList<Map<String, String>>();

                    for (var validationFailure : headerValidationFailures) {
                        var validationFailureCase = Map.of(
                                "path", validationFailure.path,
                                "reason", validationFailure.reason);
                        validationFailureCases.add(validationFailureCase);
                    }
                    throw new JApiError("error._InvalidRequestHeaders", Map.of("cases", validationFailureCases));
                }

                if (inputHeaders.containsKey("_bin")) {
                    List<Object> binaryChecksums = (List<Object>) inputHeaders.get("_bin");

                    if (binaryChecksums.isEmpty() || !binaryChecksums.contains(binaryEncoder.checksum)) {
                        // Client is initiating handshake for binary protocol
                        outputHeaders.put("_includeBinaryEncoding", true);
                    }

                    outputHeaders.put("_serializeAsBinary", true);
                }

                var clientKnownBinaryChecksums = inputHeaders.get("_clientKnownBinaryChecksums");
                if (clientKnownBinaryChecksums != null) {
                    outputHeaders.put("_clientKnownBinaryChecksums", clientKnownBinaryChecksums);
                }

                // Reflect call id
                var callId = inputHeaders.get("_id");
                if (callId != null) {
                    outputHeaders.put("_id", callId);
                }

                Map<String, Object> input;
                try {
                    input = (Map<String, Object>) inputMessage.get(2);
                } catch (ClassCastException e) {
                    throw new JApiError("error._ParseFailure", Map.of("reason", "BodyMustBeObject"));
                }

                var functionDef = jApi.get(inputTarget);

                FunctionDefinition functionDefinition;
                if (functionDef instanceof FunctionDefinition f) {
                    functionDefinition = f;
                } else {
                    throw new JApiError("error._UnknownFunction", Map.of());
                }

                var inputValidationFailures = validateStruct(functionDefinition.name,
                        functionDefinition.inputStruct.fields, input);
                if (!inputValidationFailures.isEmpty()) {
                    var validationFailureCases = new ArrayList<Map<String, String>>();
                    for (var validationFailure : inputValidationFailures) {
                        var validationFailureCase = Map.of(
                                "path", validationFailure.path,
                                "reason", validationFailure.reason);
                        validationFailureCases.add(validationFailureCase);
                    }
                    throw new JApiError("error._InvalidRequestBody", Map.of("cases", validationFailureCases));
                }

                var context = new Context(functionName);
                var contextPropertiesFromHeaders = extractContextProperties.apply(inputHeaders);
                context.properties.putAll(contextPropertiesFromHeaders);

                var unsafeOutputEnabled = Objects.equals(true, inputHeaders.get("_unsafe"));

                Map<String, Object> output;
                try {
                    if (functionName.equals("_ping")) {
                        output = Map.of();
                    } else if (functionName.equals("_jApi")) {
                        output = Map.of("jApi", originalJApiAsParsedJson);
                    } else {
                        output = handler.apply(context, input);
                    }
                } catch (JApiError e) {
                    if (functionDefinition.allowedErrors.contains(e.target)) {
                        var def = (ErrorDefinition) jApi.get(e.target);
                        var errorValidationFailures = validateStruct(e.target, def.fields, e.body);
                        if (!errorValidationFailures.isEmpty() && !unsafeOutputEnabled) {
                            var validationFailureCases = new ArrayList<Map<String, String>>();
                            for (var validationFailure : errorValidationFailures) {
                                var validationFailureCase = Map.of(
                                        "path", validationFailure.path,
                                        "reason", validationFailure.reason);
                                validationFailureCases.add(validationFailureCase);
                            }
                            throw new JApiError("error._InvalidResponseBody", Map.of("cases", validationFailureCases));
                        }

                        throw e;
                    } else {
                        throw new DisallowedError(e);
                    }
                }

                var outputValidationFailures = validateStruct(functionDefinition.name,
                        functionDefinition.outputStruct.fields,
                        output);
                if (!outputValidationFailures.isEmpty() && !unsafeOutputEnabled) {
                    var validationFailureCases = new ArrayList<Map<String, String>>();
                    for (var validationFailure : outputValidationFailures) {
                        var validationFailureCase = Map.of(
                                "path", validationFailure.path,
                                "reason", validationFailure.reason);
                        validationFailureCases.add(validationFailureCase);
                    }
                    throw new JApiError("error._InvalidResponseBody", Map.of("cases", validationFailureCases));
                }

                Map<String, Object> finalOutput;
                if (inputHeaders.containsKey("_selectFields")) {
                    Map<String, List<String>> selectStructFieldsHeader = (Map<String, List<String>>) inputHeaders
                            .get("_selectFields");
                    finalOutput = (Map<String, Object>) selectStructFields(functionDefinition.outputStruct, output,
                            selectStructFieldsHeader);
                } else {
                    finalOutput = output;
                }

                var outputTarget = "function.%s".formatted(functionName);

                return List.of(outputTarget, outputHeaders, finalOutput);
            } catch (Exception e) {
                try {
                    onError.accept(e);
                } catch (Exception ignored) {
                }
                throw e;
            }
        } catch (JApiError e) {
            throw e;
        } catch (Exception e) {
            var outputTarget = "error._ApplicationFailure";

            return List.of(outputTarget, outputHeaders, Map.of());
        }
    }

    private static List<ValidationFailure> validateHeaders(
            Map<String, Object> headers, Map<String, Definition> jApi) {
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
                validationFailures.add(new ValidationFailure("_bin", "BinaryHeaderMustBeArrayOfIntegers"));
            }
        }

        if (headers.containsKey("_selectFields")) {
            Map<String, Object> selectStructFieldsHeader = new HashMap<>();
            try {
                selectStructFieldsHeader = (Map<String, Object>) headers
                        .get("_selectFields");

            } catch (ClassCastException e) {
                validationFailures.add(new ValidationFailure("_selectFields",
                        "SelectHeaderMustBeObject"));
            }
            for (Map.Entry<String, Object> entry : selectStructFieldsHeader.entrySet()) {
                var structName = entry.getKey();
                if (!structName.startsWith("struct.")) {
                    validationFailures.add(new ValidationFailure("_selectFields{%s}".formatted(structName),
                            "SelectHeaderKeyMustBeStructReference"));
                    continue;
                }
                var structReference = jApi.get(structName);
                if (structReference == null) {
                    validationFailures.add(new ValidationFailure("_selectFields{%s}".formatted(structName),
                            "UnknownStruct"));
                    continue;
                }

                List<Object> fields = new ArrayList<>();
                try {
                    fields = (List<Object>) entry.getValue();
                } catch (ClassCastException e) {
                    validationFailures.add(new ValidationFailure("_selectFields{%s}".formatted(structName),
                            "SelectHeaderFieldsMustBeArray"));
                }

                for (int i = 0; i < fields.size(); i += 1) {
                    var field = fields.get(i);
                    String stringField;
                    try {
                        stringField = (String) field;
                    } catch (ClassCastException e) {
                        validationFailures.add(new ValidationFailure(
                                "_selectFields{%s}[%d]".formatted(structName, i),
                                "SelectHeaderFieldMustBeString"));
                        continue;
                    }
                    if (structReference instanceof TypeDefinition d) {
                        if (d.type instanceof Struct s) {
                            if (!s.fields.containsKey(stringField)) {
                                validationFailures.add(new ValidationFailure(
                                        "_selectFields{%s}[%d]".formatted(structName, i),
                                        "UnknownStructField"));
                            }
                        }
                    }
                }
            }

        }

        return validationFailures;
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
                    ValidationErrors.REQUIRED_STRUCT_FIELD_MISSING);
            validationFailures
                    .add(validationFailure);
        }

        for (Map.Entry<String, Object> entry : actualStruct.entrySet()) {
            var fieldName = entry.getKey();
            var field = entry.getValue();
            var referenceField = referenceStruct.get(fieldName);
            if (referenceField == null) {
                var validationFailure = new ValidationFailure("%s.%s".formatted(path, fieldName),
                        ValidationErrors.EXTRA_STRUCT_FIELD_NOT_ALLOWED);
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
            String namespace,
            Map<String, Struct> reference,
            String enumCase,
            Map<String, Object> actual) {
        var validationFailures = new ArrayList<ValidationFailure>();

        var referenceField = reference.get(enumCase);
        if (referenceField == null) {
            return Collections
                    .singletonList(new ValidationFailure("%s.%s".formatted(namespace, enumCase),
                            ValidationErrors.UNKNOWN_ENUM_VALUE));
        }

        var nestedValidationFailures = validateStruct("%s.%s".formatted(namespace, enumCase), referenceField.fields,
                actual);
        validationFailures.addAll(nestedValidationFailures);

        return validationFailures;
    }

    private static List<ValidationFailure> validateType(String fieldName, TypeDeclaration typeDeclaration,
            Object value) {
        if (value == null) {
            if (!typeDeclaration.nullable) {
                return Collections.singletonList(new ValidationFailure(fieldName,
                        ValidationErrors.NULL_INVALID_FOR_NON_NULL_TYPE));
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
                            new ValidationFailure(fieldName, ValidationErrors.NUMBER_INVALID_FOR_BOOLEAN_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.STRING_INVALID_FOR_BOOLEAN_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.ARRAY_INVALID_FOR_BOOLEAN_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.OBJECT_INVALID_FOR_BOOLEAN_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.VALUE_INVALID_FOR_BOOLEAN_TYPE));
                }
            } else if (expectedType instanceof JsonInteger) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.BOOLEAN_INVALID_FOR_INTEGER_TYPE));
                } else if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.NUMBER_OUT_OF_RANGE));
                } else if (value instanceof Number) {
                    if (value instanceof Long || value instanceof Integer) {
                        return Collections.emptyList();
                    } else {
                        return Collections.singletonList(new ValidationFailure(fieldName,
                                ValidationErrors.NUMBER_INVALID_FOR_INTEGER_TYPE));
                    }
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.STRING_INVALID_FOR_INTEGER_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.ARRAY_INVALID_FOR_INTEGER_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.OBJECT_INVALID_FOR_INTEGER_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.VALUE_INVALID_FOR_INTEGER_TYPE));
                }
            } else if (expectedType instanceof JsonNumber) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.BOOLEAN_INVALID_FOR_NUMBER_TYPE));
                } else if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.NUMBER_OUT_OF_RANGE));
                } else if (value instanceof Number) {
                    return Collections.emptyList();
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.STRING_INVALID_FOR_NUMBER_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.ARRAY_INVALID_FOR_NUMBER_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.OBJECT_INVALID_FOR_NUMBER_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.OBJECT_INVALID_FOR_NUMBER_TYPE));
                }
            } else if (expectedType instanceof JsonString) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.BOOLEAN_INVALID_FOR_STRING_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.NUMBER_INVALID_FOR_STRING_TYPE));
                } else if (value instanceof String) {
                    return Collections.emptyList();
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.ARRAY_INVALID_FOR_STRING_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.OBJECT_INVALID_FOR_STRING_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.VALUE_INVALID_FOR_STRING_TYPE));
                }
            } else if (expectedType instanceof JsonArray a) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.BOOLEAN_INVALID_FOR_ARRAY_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.NUMBER_INVALID_FOR_ARRAY_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.STRING_INVALID_FOR_ARRAY_TYPE));
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
                            new ValidationFailure(fieldName, ValidationErrors.OBJECT_INVALID_FOR_ARRAY_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.VALUE_INVALID_FOR_ARRAY_TYPE));
                }
            } else if (expectedType instanceof JsonObject o) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.BOOLEAN_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.NUMBER_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.STRING_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.ARRAY_INVALID_FOR_OBJECT_TYPE));
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
                            new ValidationFailure(fieldName, ValidationErrors.VALUE_INVALID_FOR_OBJECT_TYPE));
                }
            } else if (expectedType instanceof Struct s) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.BOOLEAN_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.NUMBER_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.STRING_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.ARRAY_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof Map<?, ?> m) {
                    return validateStruct(fieldName, s.fields, (Map<String, Object>) m);
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.VALUE_INVALID_FOR_STRUCT_TYPE));
                }
            } else if (expectedType instanceof Enum u) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.BOOLEAN_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.NUMBER_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.STRING_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.ARRAY_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof Map<?, ?> m) {
                    if (m.size() != 1) {
                        return Collections.singletonList(
                                new ValidationFailure(fieldName,
                                        ValidationErrors.MULTI_ENTRY_OBJECT_INVALID_FOR_ENUM_TYPE));
                    }
                    var entry = m.entrySet().stream().findFirst().get();
                    var enumCase = (String) entry.getKey();
                    var enumValue = entry.getValue();

                    if (enumValue instanceof Boolean) {
                        return Collections.singletonList(new ValidationFailure(fieldName,
                                ValidationErrors.BOOLEAN_INVALID_FOR_ENUM_STRUCT_TYPE));
                    } else if (enumValue instanceof Number) {
                        return Collections.singletonList(new ValidationFailure(fieldName,
                                ValidationErrors.NUMBER_INVALID_FOR_ENUM_STRUCT_TYPE));
                    } else if (enumValue instanceof String) {
                        return Collections.singletonList(new ValidationFailure(fieldName,
                                ValidationErrors.STRING_INVALID_FOR_ENUM_STRUCT_TYPE));
                    } else if (enumValue instanceof List) {
                        return Collections.singletonList(new ValidationFailure(fieldName,
                                ValidationErrors.ARRAY_INVALID_FOR_ENUM_STRUCT_TYPE));
                    } else if (enumValue instanceof Map<?, ?> m2) {
                        return validateEnum(fieldName, u.values, enumCase, (Map<String, Object>) m2);
                    } else {
                        return Collections.singletonList(new ValidationFailure(fieldName,
                                ValidationErrors.VALUE_INVALID_FOR_ENUM_STRUCT_TYPE));
                    }
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, ValidationErrors.VALUE_INVALID_FOR_ENUM_TYPE));
                }
            } else if (expectedType instanceof JsonAny a) {
                // all values are valid for any
                return Collections.emptyList();
            } else {
                return Collections.singletonList(new ValidationFailure(fieldName, ValidationErrors.INVALID_TYPE));
            }
        }
    }

    static Object selectStructFields(Type type, Object value, Map<String, List<String>> selectedStructFields) {
        if (type instanceof Struct s) {
            var selectedFields = selectedStructFields.get(s.name);
            var valueAsMap = (Map<String, Object>) value;
            var finalMap = new HashMap<>();
            for (var entry : valueAsMap.entrySet()) {
                if (selectedFields == null || selectedFields.contains(entry.getKey())) {
                    var field = s.fields.get(entry.getKey());
                    var valueWithSelectedFields = selectStructFields(field.typeDeclaration.type, entry.getValue(),
                            selectedStructFields);
                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }
            return finalMap;
        } else if (type instanceof Enum e) {
            var valueAsMap = (Map<String, Object>) value;
            var enumEntry = valueAsMap.entrySet().stream().findFirst().get();
            var structReference = e.values.get(enumEntry.getKey());
            Map<String, Object> newStruct = new HashMap<>();
            for (var structEntry : structReference.fields.entrySet()) {
                var valueWithSelectedFields = selectStructFields(structEntry.getValue().typeDeclaration.type,
                        enumEntry.getValue(),
                        selectedStructFields);
                newStruct.put(structEntry.getKey(), valueWithSelectedFields);
            }
            return Map.of(enumEntry.getKey(), newStruct);
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

    static boolean inputIsJson(byte[] inputJapiMessageBytes) {
        return inputJapiMessageBytes[0] == '[';
    }

    static List<Object> deserialize(byte[] inputJapiMessageBytes, SerializationStrategy serializer,
            BinaryEncoder binaryEncoder) {
        if (inputIsJson(inputJapiMessageBytes)) {
            try {
                return serializer.fromJson(inputJapiMessageBytes);
            } catch (DeserializationError e) {
                throw new JApiError("error._ParseFailure", Map.of());
            }
        } else {
            try {
                var encodedInputJapiMessage = serializer.fromMsgPack(inputJapiMessageBytes);
                if (encodedInputJapiMessage.size() < 3) {
                    throw new JApiError("error._ParseFailure",
                            Map.of("reason", "JapiMessageArrayMustHaveThreeElements"));
                }
                return binaryEncoder.decode(encodedInputJapiMessage);
                // } catch (BinaryChecksumMismatchException e) {
                // throw new JApiError("error._BinaryDecodeFailure", Map.of());
            } catch (DeserializationError e) {
                throw new JApiError("error._ParseFailure", Map.of(), e);
            }
        }
    }
}
