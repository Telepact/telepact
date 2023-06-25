package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.BiFunction;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.regex.Pattern;

class InternalProcess {

    static List<Object> processObject(List<Object> inputJapiMessage, Consumer<Throwable> onError,
            BinaryEncoder binaryEncoder,
            Map<String, Definition> apiDescription,
            BiFunction<Context, Map<String, Object>, Map<String, Object>> internalHandler,
            BiFunction<Context, Map<String, Object>, Map<String, Object>> handler,
            Function<Map<String, Object>, Map<String, Object>> extractContextProperties) {
        var finalHeaders = new HashMap<String, Object>();
        try {
            try {
                if (inputJapiMessage.size() < 3) {
                    throw new JApiError("error._ParseFailure", Map.of("reason", "MessageMustHaveThreeElements"));
                }

                String messageType;
                try {
                    messageType = (String) inputJapiMessage.get(0);
                } catch (ClassCastException e) {
                    throw new JApiError("error._ParseFailure", Map.of("reason", "MessageTypeMustBeStringType"));
                }

                var regex = Pattern.compile("^function\\.([a-zA-Z_]\\w*)(.input)?");
                var matcher = regex.matcher(messageType);
                if (!matcher.matches()) {
                    throw new JApiError("error._ParseFailure", Map.of("reason", "MessageTypeStringMustBeFunction"));
                }
                var functionName = matcher.group(1);

                Map<String, Object> headers;
                try {
                    headers = (Map<String, Object>) inputJapiMessage.get(1);
                } catch (ClassCastException e) {
                    throw new JApiError("error._ParseFailure", Map.of("reason", "MessageHeaderMustBeObject"));
                }

                if (headers.containsKey("_bin")) {
                    List<Object> binaryChecksums;
                    try {
                        binaryChecksums = (List<Object>) headers.get("_bin");
                    } catch (Exception e) {
                        throw new JApiError("error._ParseFailure", Map.of("reason", "BinaryHeaderMustBeArray"));
                    }

                    if (binaryChecksums.isEmpty() || !binaryChecksums.contains(binaryEncoder.checksum)) {
                        // Client is initiating handshake for binary protocol
                        finalHeaders.put("_binaryEncoding", binaryEncoder.encodeMap);
                    }

                    finalHeaders.put("_bin", List.of(binaryEncoder.checksum));
                }

                // Reflect call id
                var callId = headers.get("_id");
                if (callId != null) {
                    finalHeaders.put("_id", callId);
                }

                Map<String, Object> input;
                try {
                    input = (Map<String, Object>) inputJapiMessage.get(2);
                } catch (ClassCastException e) {
                    throw new JApiError("error._ParseFailure", Map.of("reason", "MessageBodyMustBeObject"));
                }

                var functionDef = apiDescription.get(messageType);

                FunctionDefinition functionDefinition;
                if (functionDef instanceof FunctionDefinition f) {
                    functionDefinition = f;
                } else {
                    throw new JApiError("error._UnknownFunction", Map.of());
                }

                Map<String, List<String>> slicedTypes = null;
                if (headers.containsKey("_selectFields")) {
                    try {
                        slicedTypes = (Map<String, List<String>>) headers.get("_selectFields");
                        for (Map.Entry<String, List<String>> entry : slicedTypes.entrySet()) {
                            var fields = entry.getValue();
                            for (var field : fields) {
                                // verify the cast works
                                var stringField = (String) field;
                            }
                        }
                    } catch (ClassCastException e) {
                        throw new JApiError("error._ParseFailure",
                                Map.of("reason", "SelectStructFieldsHeaderMustBeObjectOfArraysOfStrings"));
                    }
                }

                var inputValidationFailures = validateStruct("input", functionDefinition.inputStruct().fields(), input);
                if (!inputValidationFailures.isEmpty()) {
                    var validationFailureCases = new ArrayList<Map<String, String>>();
                    for (var validationFailure : inputValidationFailures) {
                        var validationFailureCase = Map.of(
                                "field", validationFailure.path,
                                "reason", validationFailure.reason);
                        validationFailureCases.add(validationFailureCase);
                    }
                    throw new JApiError("error._InvalidInput", Map.of("cases", validationFailureCases));
                }

                var context = new Context(functionName);
                var contextPropertiesFromHeaders = extractContextProperties.apply(headers);
                context.properties.putAll(contextPropertiesFromHeaders);

                Map<String, Object> output;
                try {
                    if (functionName.startsWith("_")) {
                        output = internalHandler.apply(context, input);
                    } else {
                        output = handler.apply(context, input);
                    }
                } catch (JApiError e) {
                    if (functionDefinition.errors().contains(e.target)) {
                        var def = (ErrorDefinition) apiDescription.get(e.target);
                        var errorValidationFailures = validateStruct(e.target, def.fields(), e.body);
                        if (!errorValidationFailures.isEmpty()) {
                            var validationFailureCases = new ArrayList<Map<String, String>>();
                            for (var validationFailure : errorValidationFailures) {
                                var validationFailureCase = Map.of(
                                        "field", validationFailure.path,
                                        "reason", validationFailure.reason);
                                validationFailureCases.add(validationFailureCase);
                            }
                            // TODO: Show the output validation cases. Obscurity is not security here.
                            // throw new JApiError("error._InvalidOutput", Map.of("cases",
                            // validationFailureCases));
                            throw new JApiError("error._InvalidOutput", Map.of());
                        }

                        throw e;
                    } else {
                        throw new DisallowedError(e);
                    }
                }

                var outputValidationFailures = validateStruct("output", functionDefinition.outputStruct().fields(),
                        output);
                if (!outputValidationFailures.isEmpty()) {
                    var validationFailureCases = new ArrayList<Map<String, String>>();
                    for (var validationFailure : outputValidationFailures) {
                        var validationFailureCase = Map.of(
                                "field", validationFailure.path,
                                "reason", validationFailure.reason);
                        validationFailureCases.add(validationFailureCase);
                    }
                    // TODO: Show the output validation cases. Obscurity is not security here.
                    // throw new JApiError("error._InvalidOutput", Map.of("cases",
                    // validationFailureCases));
                    throw new JApiError("error._InvalidOutput", Map.of());
                }

                Map<String, Object> finalOutput;
                if (slicedTypes != null) {
                    finalOutput = (Map<String, Object>) sliceTypes(functionDefinition.outputStruct(), output,
                            slicedTypes);
                } else {
                    finalOutput = output;
                }

                var outputMessageType = "function.%s".formatted(functionName);

                return List.of(outputMessageType, finalHeaders, finalOutput);
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
            var messageType = "error._ApplicationFailure";

            return List.of(messageType, finalHeaders, Map.of());
        }
    }

    private static List<ValidationFailure> validateStruct(
            String namespace,
            Map<String, FieldDeclaration> referenceStruct,
            Map<String, Object> actualStruct) {
        var validationFailures = new ArrayList<ValidationFailure>();

        var missingFields = new ArrayList<String>();
        for (Map.Entry<String, FieldDeclaration> entry : referenceStruct.entrySet()) {
            var fieldName = entry.getKey();
            var fieldDeclaration = entry.getValue();
            if (!actualStruct.containsKey(fieldName) && !fieldDeclaration.optional()) {
                missingFields.add(fieldName);
            }
        }

        for (var missingField : missingFields) {
            var validationFailure = new ValidationFailure("%s.%s".formatted(namespace, missingField),
                    InvalidFieldTypeError.REQUIRED_STRUCT_FIELD_MISSING);
            validationFailures
                    .add(validationFailure);
        }

        for (Map.Entry<String, Object> entry : actualStruct.entrySet()) {
            var fieldName = entry.getKey();
            var field = entry.getValue();
            var referenceField = referenceStruct.get(fieldName);
            if (referenceField == null) {
                var validationFailure = new ValidationFailure("%s.%s".formatted(namespace, fieldName),
                        InvalidFieldTypeError.EXTRA_STRUCT_FIELD_NOT_ALLOWED);
                validationFailures
                        .add(validationFailure);
                continue;
            }
            var nestedValidationFailures = validateType("%s.%s".formatted(namespace, fieldName),
                    referenceField.typeDeclaration(), field);
            validationFailures.addAll(nestedValidationFailures);
        }

        return validationFailures;
    }

    private static List<ValidationFailure> validateType(String fieldName, TypeDeclaration typeDeclaration,
            Object value) {
        if (value == null) {
            if (!typeDeclaration.nullable()) {
                return Collections.singletonList(new ValidationFailure(fieldName,
                        InvalidFieldTypeError.NULL_INVALID_FOR_NON_NULL_TYPE));
            } else {
                return Collections.emptyList();
            }
        } else {
            var expectedType = typeDeclaration.type();
            if (expectedType instanceof JsonBoolean) {
                if (value instanceof Boolean) {
                    return Collections.emptyList();
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_BOOLEAN_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_BOOLEAN_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_BOOLEAN_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_BOOLEAN_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_BOOLEAN_TYPE));
                }
            } else if (expectedType instanceof JsonInteger) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_INTEGER_TYPE));
                } else if (value instanceof Number) {
                    if (value instanceof Long || value instanceof Integer) {
                        return Collections.emptyList();
                    } else {
                        return Collections.singletonList(new ValidationFailure(fieldName,
                                InvalidFieldTypeError.NUMBER_INVALID_FOR_INTEGER_TYPE));
                    }
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_INTEGER_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_INTEGER_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_INTEGER_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_INTEGER_TYPE));
                }
            } else if (expectedType instanceof JsonNumber) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_NUMBER_TYPE));
                } else if (value instanceof Number) {
                    return Collections.emptyList();
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_NUMBER_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_NUMBER_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_NUMBER_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_NUMBER_TYPE));
                }
            } else if (expectedType instanceof JsonString) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_STRING_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_STRING_TYPE));
                } else if (value instanceof String) {
                    return Collections.emptyList();
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_STRING_TYPE));
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_STRING_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_STRING_TYPE));
                }
            } else if (expectedType instanceof JsonArray a) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ARRAY_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_ARRAY_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_ARRAY_TYPE));
                } else if (value instanceof List l) {
                    var validationFailures = new ArrayList<ValidationFailure>();
                    for (var i = 0; i < l.size(); i += 1) {
                        var element = l.get(i);
                        var nestedValidationFailures = validateType("%s[%s]".formatted(fieldName, i), a.nestedType(),
                                element);
                        validationFailures.addAll(nestedValidationFailures);
                    }
                    return validationFailures;
                } else if (value instanceof Map) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_ARRAY_TYPE));
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_ARRAY_TYPE));
                }
            } else if (expectedType instanceof JsonObject o) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_OBJECT_TYPE));
                } else if (value instanceof Map<?, ?> m) {
                    var validationFailures = new ArrayList<ValidationFailure>();
                    for (Map.Entry<?, ?> entry : m.entrySet()) {
                        var k = (String) entry.getKey();
                        var v = entry.getValue();
                        var nestedValidationFailures = validateType("%s{%s}".formatted(fieldName, k), o.nestedType(),
                                v);
                        validationFailures.addAll(nestedValidationFailures);
                    }
                    return validationFailures;
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_OBJECT_TYPE));
                }
            } else if (expectedType instanceof Struct s) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_STRUCT_TYPE));
                } else if (value instanceof Map<?, ?> m) {
                    return validateStruct(fieldName, s.fields(), (Map<String, Object>) m);
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_STRUCT_TYPE));
                }
            } else if (expectedType instanceof Enum u) {
                if (value instanceof Boolean) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof Number) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof String) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof List) {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_ENUM_TYPE));
                } else if (value instanceof Map<?, ?> m) {
                    if (m.size() != 1) {
                        return Collections.singletonList(
                                new ValidationFailure(fieldName,
                                        InvalidFieldTypeError.MULTI_ENTRY_OBJECT_INVALID_FOR_ENUM_TYPE));
                    }
                    var entry = m.entrySet().stream().findFirst().get();
                    var enumCase = (String) entry.getKey();
                    var enumValue = entry.getValue();

                    if (enumValue instanceof Boolean) {
                        return Collections.singletonList(new ValidationFailure(fieldName,
                                InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ENUM_STRUCT_TYPE));
                    } else if (enumValue instanceof Number) {
                        return Collections.singletonList(new ValidationFailure(fieldName,
                                InvalidFieldTypeError.NUMBER_INVALID_FOR_ENUM_STRUCT_TYPE));
                    } else if (enumValue instanceof String) {
                        return Collections.singletonList(new ValidationFailure(fieldName,
                                InvalidFieldTypeError.STRING_INVALID_FOR_ENUM_STRUCT_TYPE));
                    } else if (enumValue instanceof List) {
                        return Collections.singletonList(new ValidationFailure(fieldName,
                                InvalidFieldTypeError.ARRAY_INVALID_FOR_ENUM_STRUCT_TYPE));
                    } else if (enumValue instanceof Map<?, ?> m2) {
                        return validateEnum(fieldName, u.cases(), enumCase, (Map<String, Object>) m2);
                    } else {
                        return Collections.singletonList(new ValidationFailure(fieldName,
                                InvalidFieldTypeError.VALUE_INVALID_FOR_ENUM_STRUCT_TYPE));
                    }
                } else {
                    return Collections.singletonList(
                            new ValidationFailure(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_ENUM_TYPE));
                }
            } else if (expectedType instanceof JsonAny a) {
                // all values validate for any
                return Collections.emptyList();
            } else {
                return Collections.singletonList(new ValidationFailure(fieldName, InvalidFieldTypeError.INVALID_TYPE));
            }
        }
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
                            InvalidFieldTypeError.UNKNOWN_ENUM_VALUE));
        }

        var nestedValidationFailures = validateStruct("%s.%s".formatted(namespace, enumCase), referenceField.fields(),
                actual);
        validationFailures.addAll(nestedValidationFailures);

        return validationFailures;
    }

    static Object sliceTypes(Type type, Object value, Map<String, List<String>> slicedTypes) {
        if (type instanceof Struct s) {
            var slicedFields = slicedTypes.get(s.name());
            var valueAsMap = (Map<String, Object>) value;
            var finalMap = new HashMap<>();
            for (var entry : valueAsMap.entrySet()) {
                if (slicedFields == null || slicedFields.contains(entry.getKey())) {
                    var field = s.fields().get(entry.getKey());
                    var slicedValue = sliceTypes(field.typeDeclaration().type(), entry.getValue(), slicedTypes);
                    finalMap.put(entry.getKey(), slicedValue);
                }
            }
            return finalMap;
        } else if (type instanceof Enum e) {
            var valueAsMap = (Map<String, Object>) value;
            var enumEntry = valueAsMap.entrySet().stream().findFirst().get();
            var structReference = e.cases().get(enumEntry.getKey());
            Map<String, Object> newStruct = new HashMap<>();
            for (var structEntry : structReference.fields().entrySet()) {
                var slicedValue = sliceTypes(structEntry.getValue().typeDeclaration().type(), enumEntry.getValue(),
                        slicedTypes);
                newStruct.put(structEntry.getKey(), slicedValue);
            }
            return Map.of(enumEntry.getKey(), newStruct);
        } else if (type instanceof JsonObject o) {
            var valueAsMap = (Map<String, Object>) value;
            var finalMap = new HashMap<>();
            for (var entry : valueAsMap.entrySet()) {
                var slicedValue = sliceTypes(o.nestedType().type(), entry.getValue(), slicedTypes);
                finalMap.put(entry.getKey(), slicedValue);
            }
            return finalMap;
        } else if (type instanceof JsonArray a) {
            var valueAsList = (List<Object>) value;
            var finalList = new ArrayList<>();
            for (var entry : valueAsList) {
                var slicedValue = sliceTypes(a.nestedType().type(), entry, slicedTypes);
                finalList.add(slicedValue);
            }
            return finalList;
        } else {
            return value;
        }
    }

    static boolean inputIsJson(byte[] inputJapiMessagePayload) {
        return inputJapiMessagePayload[0] == '[';
    }

    static List<Object> deserialize(byte[] inputJapiMessagePayload, Serializer serializer,
            BinaryEncoder binaryEncoder) {
        if (inputIsJson(inputJapiMessagePayload)) {
            try {
                return serializer.deserializeFromJson(inputJapiMessagePayload);
            } catch (DeserializationException e) {
                throw new JApiError("error._ParseFailure", Map.of());
            }
        } else {
            try {
                var encodedInputJapiMessage = serializer.deserializeFromMsgPack(inputJapiMessagePayload);
                if (encodedInputJapiMessage.size() < 3) {
                    throw new JApiError("error._ParseFailure",
                            Map.of("reason", "JapiMessageArrayMustHaveThreeElements"));
                }
                return binaryEncoder.decode(encodedInputJapiMessage);
            } catch (BinaryChecksumMismatchException e) {
                throw new JApiError("error._BinaryDecodeFailure", Map.of());
            } catch (DeserializationException e) {
                throw new JApiError("error._ParseFailure", Map.of(), e);
            }
        }
    }
}
