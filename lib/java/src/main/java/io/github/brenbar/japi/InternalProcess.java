package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;
import java.util.function.Consumer;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

class InternalProcess {

    static byte[] process(byte[] inputJapiMessagePayload, Serializer serializer, Consumer<Throwable> onError,
            BinaryEncoder binaryEncoder, Map<String, Definition> apiDescription, Handler internalHandler,
            Handler handler) {
        List<Object> inputJapiMessage;
        boolean inputIsBinary = false;
        if (inputJapiMessagePayload[0] == '[') {
            try {
                inputJapiMessage = serializer.deserializeFromJson(inputJapiMessagePayload);
            } catch (DeserializationError e) {
                onError.accept(e);
                return serializer.serializeToJson(List.of("error._ParseFailure", Map.of(), Map.of()));
            }
        } else {
            try {
                var encodedInputJapiMessage = serializer.deserializeFromMsgPack(inputJapiMessagePayload);
                if (encodedInputJapiMessage.size() < 3) {
                    return serializer.serializeToJson(List.of("error._ParseFailure", Map.of(),
                            Map.of("reason", "JapiMessageArrayMustHaveThreeElements")));
                }
                inputJapiMessage = binaryEncoder.decode(encodedInputJapiMessage);
                inputIsBinary = true;
            } catch (IncorrectBinaryHashException e) {
                onError.accept(e);
                return serializer.serializeToJson(List.of("error._InvalidBinaryEncoding", Map.of(), Map.of()));
            } catch (DeserializationError e) {
                onError.accept(e);
                return serializer.serializeToJson(List.of("error._ParseFailure", Map.of(), Map.of()));
            }
        }

        var outputJapiMessage = processObject(inputJapiMessage, onError, binaryEncoder, apiDescription,
                internalHandler, handler);
        var headers = (Map<String, Object>) outputJapiMessage.get(1);
        var returnAsBinary = headers.containsKey("_bin");
        if (!returnAsBinary && inputIsBinary) {
            headers.put("_bin", binaryEncoder.binaryChecksum);
        }

        if (inputIsBinary || returnAsBinary) {
            var encodedOutputJapiMessage = binaryEncoder.encode(outputJapiMessage);
            return serializer.serializeToMsgPack(encodedOutputJapiMessage);
        } else {
            return serializer.serializeToJson(outputJapiMessage);
        }
    }

    private static List<Object> processObject(List<Object> inputJapiMessage, Consumer<Throwable> onError,
            BinaryEncoder binaryEncoder,
            Map<String, Definition> apiDescription, Handler internalHandler, Handler handler) {
        var finalHeaders = new HashMap<String, Object>();
        try {
            try {
                if (inputJapiMessage.size() < 3) {
                    throw new JapiMessageArrayTooFewElements();
                }

                String messageType;
                try {
                    messageType = (String) inputJapiMessage.get(0);
                } catch (ClassCastException e) {
                    throw new JapiMessageTypeNotString();
                }

                var regex = Pattern.compile("^function\\.([a-zA-Z_]\\w*)(.input)?");
                var matcher = regex.matcher(messageType);
                if (!matcher.matches()) {
                    throw new JapiMessageTypeNotFunction();
                }
                var functionName = matcher.group(1);

                Map<String, Object> headers;
                try {
                    headers = (Map<String, Object>) inputJapiMessage.get(1);
                } catch (ClassCastException e) {
                    throw new JapiMessageHeaderNotObject();
                }

                if (headers.containsKey("_bin")) {
                    List<Object> binaryChecksums;
                    try {
                        binaryChecksums = (List<Object>) headers.get("_bin");
                    } catch (Exception e) {
                        throw new JapiParseError("Japi message");
                    }

                    if (binaryChecksums.isEmpty() || !binaryChecksums.contains(binaryEncoder.binaryChecksum)) {
                        // Client is initiating handshake for binary protocol
                        finalHeaders.put("_binaryEncoding", binaryEncoder.encodeMap);
                    }

                    finalHeaders.put("_bin", List.of(binaryEncoder.binaryChecksum));
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
                    throw new JapiMessageBodyNotObject();
                }

                var functionDef = apiDescription.get(messageType);

                FunctionDefinition functionDefinition;
                if (functionDef instanceof FunctionDefinition f) {
                    functionDefinition = f;
                } else {
                    throw new FunctionNotFound(functionName);
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
                        throw new InvalidSelectFieldsHeader();
                    }
                }

                validateStruct("input", functionDefinition.inputStruct().fields(), input);

                Map<String, Object> output;
                try {
                    if (functionName.startsWith("_")) {
                        output = internalHandler.handle(functionName, headers, input);
                    } else {
                        output = handler.handle(functionName, headers, input);
                    }
                } catch (ApplicationError e) {
                    if (functionDefinition.errors().contains(e.messageType)) {
                        var def = (ErrorDefinition) apiDescription.get(e.messageType);
                        try {
                            validateStruct("error", def.fields(), e.body);
                        } catch (Exception e2) {
                            throw new InvalidApplicationFailure(e2);
                        }

                        throw e;
                    } else {
                        throw new DisallowedError(e);
                    }
                }

                try {
                    validateStruct("output", functionDefinition.outputStruct().fields(), output);
                } catch (Exception e) {
                    throw new InvalidOutput(e);
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
        } catch (StructHasExtraFields e) {
            var messageType = "error._InvalidInput";
            var errors = e.extraFields.stream()
                    .collect(Collectors.toMap(f -> "%s.%s".formatted(e.namespace, f), f -> "UnknownStructField"));
            var messageBody = createInvalidFields(errors);

            return List.of(messageType, finalHeaders, messageBody);

        } catch (StructMissingFields e) {
            var messageType = "error._InvalidInput";
            var errors = e.missingFields.stream().collect(
                    Collectors.toMap(f -> "%s.%s".formatted(e.namespace, f), f -> "RequiredStructFieldMissing"));
            var messageBody = createInvalidFields(errors);

            return List.of(messageType, finalHeaders, messageBody);

        } catch (UnknownEnumField e) {
            var messageType = "error._InvalidInput";
            var messageBody = createInvalidField("%s.%s".formatted(e.namespace, e.field),
                    "UnknownEnumField");

            return List.of(messageType, finalHeaders, messageBody);
        } catch (EnumDoesNotHaveOnlyOneField e) {
            var messageType = "error._InvalidInput";
            var messageBody = createInvalidField(e.namespace, "EnumDoesNotHaveExactlyOneField");

            return List.of(messageType, finalHeaders, messageBody);
        } catch (InvalidFieldType e) {
            var entry = createInvalidField(e);

            var messageType = entry.getKey();
            var messageBody = entry.getValue();

            return List.of(messageType, finalHeaders, messageBody);
        } catch (InvalidOutput | InvalidApplicationFailure e) {
            var messageType = "error._InvalidOutput";

            return List.of(messageType, finalHeaders, Map.of());
        } catch (InvalidInput e) {
            var messageType = "error._InvalidInput";

            return List.of(messageType, finalHeaders, Map.of());
        } catch (InvalidBinaryEncoding | BinaryDecodeFailure e) {
            var messageType = "error._InvalidBinary";

            finalHeaders.put("_binaryEncoding", binaryEncoder.encodeMap);

            return List.of(messageType, finalHeaders, Map.of());
        } catch (FunctionNotFound e) {
            var messageType = "error._UnknownFunction";

            return List.of(messageType, finalHeaders, Map.of());
        } catch (ApplicationError e) {
            var messageType = e.messageType;

            return List.of(messageType, finalHeaders, e.body);
        } catch (Exception e) {
            var messageType = "error._ApplicationFailure";

            return List.of(messageType, finalHeaders, Map.of());
        }
    }

    private static void validateStruct(
            String namespace,
            Map<String, FieldDeclaration> referenceStruct,
            Map<String, Object> actualStruct) {
        var missingFields = new ArrayList<String>();
        for (Map.Entry<String, FieldDeclaration> entry : referenceStruct.entrySet()) {
            var fieldName = entry.getKey();
            var fieldDeclaration = entry.getValue();
            if (!actualStruct.containsKey(fieldName) && !fieldDeclaration.optional()) {
                missingFields.add(fieldName);
            }
        }

        if (!missingFields.isEmpty()) {
            throw new StructMissingFields(namespace, missingFields);
        }

        var extraFields = new ArrayList<String>();
        for (Map.Entry<String, Object> entry : actualStruct.entrySet()) {
            var name = entry.getKey();
            if (!referenceStruct.containsKey(name)) {
                extraFields.add(name);
            }
        }

        if (!extraFields.isEmpty()) {
            throw new StructHasExtraFields(namespace, extraFields);
        }

        for (Map.Entry<String, Object> entry : actualStruct.entrySet()) {
            var fieldName = entry.getKey();
            var field = entry.getValue();
            var referenceField = referenceStruct.get(fieldName);
            if (referenceField == null) {
                throw new StructHasExtraFields(namespace, List.of(fieldName));
            }
            validateType("%s.%s".formatted(namespace, fieldName), referenceField.typeDeclaration(), field);
        }
    }

    private static void validateType(String fieldName, TypeDeclaration typeDeclaration, Object value) {
        if (value == null) {
            if (!typeDeclaration.nullable()) {
                throw new InvalidFieldType(fieldName, InvalidFieldTypeError.NULL_INVALID_FOR_NON_NULL_TYPE);
            } else {
                return;
            }
        } else {
            var expectedType = typeDeclaration.type();
            if (expectedType instanceof JsonBoolean) {
                if (value instanceof Boolean) {
                    return;
                } else if (value instanceof Number) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_BOOLEAN_TYPE);
                } else if (value instanceof String) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_BOOLEAN_TYPE);
                } else if (value instanceof List) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_BOOLEAN_TYPE);
                } else if (value instanceof Map) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_BOOLEAN_TYPE);
                } else {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_BOOLEAN_TYPE);
                }
            } else if (expectedType instanceof JsonInteger) {
                if (value instanceof Boolean) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_INTEGER_TYPE);
                } else if (value instanceof Number) {
                    if (value instanceof Long || value instanceof Integer) {
                        return;
                    } else {
                        throw new InvalidFieldType(fieldName,
                                InvalidFieldTypeError.NUMBER_INVALID_FOR_INTEGER_TYPE);
                    }
                } else if (value instanceof String) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_INTEGER_TYPE);
                } else if (value instanceof List) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_INTEGER_TYPE);
                } else if (value instanceof Map) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_INTEGER_TYPE);
                } else {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_INTEGER_TYPE);
                }
            } else if (expectedType instanceof JsonNumber) {
                if (value instanceof Boolean) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_NUMBER_TYPE);
                } else if (value instanceof Number) {
                    return;
                } else if (value instanceof String) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_NUMBER_TYPE);
                } else if (value instanceof List) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_NUMBER_TYPE);
                } else if (value instanceof Map) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_NUMBER_TYPE);
                } else {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_NUMBER_TYPE);
                }
            } else if (expectedType instanceof JsonString) {
                if (value instanceof Boolean) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_STRING_TYPE);
                } else if (value instanceof Number) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_STRING_TYPE);
                } else if (value instanceof String) {
                    return;
                } else if (value instanceof List) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_STRING_TYPE);
                } else if (value instanceof Map) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_STRING_TYPE);
                } else {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_STRING_TYPE);
                }
            } else if (expectedType instanceof JsonArray a) {
                if (value instanceof Boolean) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ARRAY_TYPE);
                } else if (value instanceof Number) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_ARRAY_TYPE);
                } else if (value instanceof String) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_ARRAY_TYPE);
                } else if (value instanceof List l) {
                    for (var i = 0; i < l.size(); i += 1) {
                        var element = l.get(i);
                        validateType("%s[%s]".formatted(fieldName, i), a.nestedType(), element);
                    }
                    return;
                } else if (value instanceof Map) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_ARRAY_TYPE);
                } else {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_ARRAY_TYPE);
                }
            } else if (expectedType instanceof JsonObject o) {
                if (value instanceof Boolean) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_OBJECT_TYPE);
                } else if (value instanceof Number) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_OBJECT_TYPE);
                } else if (value instanceof String) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_OBJECT_TYPE);
                } else if (value instanceof List) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_OBJECT_TYPE);
                } else if (value instanceof Map<?, ?> m) {
                    for (Map.Entry<?, ?> entry : m.entrySet()) {
                        var k = (String) entry.getKey();
                        var v = entry.getValue();
                        validateType("%s{%s}".formatted(fieldName, k), o.nestedType(), v);
                    }
                    return;
                } else {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_OBJECT_TYPE);
                }
            } else if (expectedType instanceof Struct s) {
                if (value instanceof Boolean) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_STRUCT_TYPE);
                } else if (value instanceof Number) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_STRUCT_TYPE);
                } else if (value instanceof String) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_STRUCT_TYPE);
                } else if (value instanceof List) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_STRUCT_TYPE);
                } else if (value instanceof Map<?, ?> m) {
                    validateStruct(fieldName, s.fields(), (Map<String, Object>) m);
                    return;
                } else {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_STRUCT_TYPE);
                }
            } else if (expectedType instanceof Enum u) {
                if (value instanceof Boolean) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ENUM_TYPE);
                } else if (value instanceof Number) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_ENUM_TYPE);
                } else if (value instanceof String) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_ENUM_TYPE);
                } else if (value instanceof List) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_ENUM_TYPE);
                } else if (value instanceof Map<?, ?> m) {
                    if (m.size() != 1) {
                        throw new EnumDoesNotHaveOnlyOneField(fieldName);
                    }
                    var entry = m.entrySet().stream().findFirst().get();
                    var enumCase = (String) entry.getKey();
                    var enumValue = entry.getValue();

                    if (enumValue instanceof Boolean) {
                        throw new InvalidFieldType(fieldName,
                                InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ENUM_STRUCT_TYPE);
                    } else if (enumValue instanceof Number) {
                        throw new InvalidFieldType(fieldName,
                                InvalidFieldTypeError.NUMBER_INVALID_FOR_ENUM_STRUCT_TYPE);
                    } else if (enumValue instanceof String) {
                        throw new InvalidFieldType(fieldName,
                                InvalidFieldTypeError.STRING_INVALID_FOR_ENUM_STRUCT_TYPE);
                    } else if (enumValue instanceof List) {
                        throw new InvalidFieldType(fieldName,
                                InvalidFieldTypeError.ARRAY_INVALID_FOR_ENUM_STRUCT_TYPE);
                    } else if (enumValue instanceof Map<?, ?> m2) {
                        validateEnum(fieldName, u.cases(), enumCase, (Map<String, Object>) m2);
                        return;
                    } else {
                        throw new InvalidFieldType(fieldName,
                                InvalidFieldTypeError.VALUE_INVALID_FOR_ENUM_STRUCT_TYPE);
                    }
                } else {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_ENUM_TYPE);
                }
            } else if (expectedType instanceof JsonAny a) {
                // all values validate for any
            } else {
                throw new InvalidFieldType(fieldName, InvalidFieldTypeError.INVALID_TYPE);
            }
        }
    }

    private static void validateEnum(
            String namespace,
            Map<String, Struct> reference,
            String enumCase,
            Map<String, Object> actual) {
        var referenceField = reference.get(enumCase);
        if (referenceField == null) {
            throw new UnknownEnumField(namespace, enumCase);
        }

        validateStruct("%s.%s".formatted(namespace, enumCase), referenceField.fields(), actual);
    }

    static Map.Entry<String, Map<String, List<Map<String, String>>>> createInvalidField(InvalidFieldType e) {
        var entry = switch (e.error) {
            case NULL_INVALID_FOR_NON_NULL_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "NullInvalidForNonNullType"));

            case NUMBER_INVALID_FOR_BOOLEAN_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "NumberInvalidForBooleanType"));

            case STRING_INVALID_FOR_BOOLEAN_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "StringInvalidForBooleanType"));

            case ARRAY_INVALID_FOR_BOOLEAN_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ArrayInvalidForBooleanType"));

            case OBJECT_INVALID_FOR_BOOLEAN_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ObjectInvalidForBooleanType"));

            case VALUE_INVALID_FOR_BOOLEAN_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ValueInvalidForBooleanType"));

            case BOOLEAN_INVALID_FOR_INTEGER_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "BooleanInvalidForIntegerType"));

            case NUMBER_INVALID_FOR_INTEGER_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "NumberInvalidForIntegerType"));

            case STRING_INVALID_FOR_INTEGER_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "StringInvalidForIntegerType"));

            case ARRAY_INVALID_FOR_INTEGER_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ArrayInvalidForIntegerType"));

            case OBJECT_INVALID_FOR_INTEGER_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ObjectInvalidForIntegerType"));

            case VALUE_INVALID_FOR_INTEGER_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ValueInvalidForIntegerType"));

            case BOOLEAN_INVALID_FOR_NUMBER_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "BooleanInvalidForNumberType"));

            case STRING_INVALID_FOR_NUMBER_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "StringInvalidForNumberType"));

            case ARRAY_INVALID_FOR_NUMBER_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ArrayInvalidForNumberType"));

            case OBJECT_INVALID_FOR_NUMBER_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ObjectInvalidForNumberType"));

            case VALUE_INVALID_FOR_NUMBER_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ValueInvalidForNumberType"));

            case BOOLEAN_INVALID_FOR_STRING_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "BooleanInvalidForStringType"));

            case NUMBER_INVALID_FOR_STRING_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "NumberInvalidForStringType"));

            case ARRAY_INVALID_FOR_STRING_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ArrayInvalidForStringType"));

            case OBJECT_INVALID_FOR_STRING_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ObjectInvalidForStringType"));

            case VALUE_INVALID_FOR_STRING_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ValueInvalidForStringType"));

            case BOOLEAN_INVALID_FOR_ARRAY_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "BooleanInvalidForArrayType"));

            case NUMBER_INVALID_FOR_ARRAY_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "NumberInvalidForArrayType"));

            case STRING_INVALID_FOR_ARRAY_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "StringInvalidForArrayType"));

            case OBJECT_INVALID_FOR_ARRAY_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ObjectInvalidForArrayType"));

            case VALUE_INVALID_FOR_ARRAY_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ValueInvalidForArrayType"));

            case BOOLEAN_INVALID_FOR_OBJECT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "BooleanInvalidForObjectType"));

            case NUMBER_INVALID_FOR_OBJECT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "NumberInvalidForObjectType"));

            case STRING_INVALID_FOR_OBJECT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "StringInvalidForObjectType"));

            case ARRAY_INVALID_FOR_OBJECT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ArrayInvalidForObjectType"));

            case VALUE_INVALID_FOR_OBJECT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ValueInvalidForObjectType"));

            case BOOLEAN_INVALID_FOR_STRUCT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "BooleanInvalidForStructType"));

            case NUMBER_INVALID_FOR_STRUCT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "NumberInvalidForStructType"));

            case STRING_INVALID_FOR_STRUCT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "StringInvalidForStructType"));

            case ARRAY_INVALID_FOR_STRUCT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ArrayInvalidForStructType"));

            case VALUE_INVALID_FOR_STRUCT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ValueInvalidForStructType"));

            case BOOLEAN_INVALID_FOR_ENUM_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "BooleanInvalidForEnumType"));

            case NUMBER_INVALID_FOR_ENUM_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "NumberInvalidForEnumType"));

            case STRING_INVALID_FOR_ENUM_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "StringInvalidForEnumType"));

            case ARRAY_INVALID_FOR_ENUM_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ArrayInvalidForEnumType"));

            case VALUE_INVALID_FOR_ENUM_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ValueInvalidForEnumType"));

            case BOOLEAN_INVALID_FOR_ENUM_STRUCT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "BooleanInvalidForEnumStructType"));

            case NUMBER_INVALID_FOR_ENUM_STRUCT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "NumberInvalidForEnumStructType"));

            case STRING_INVALID_FOR_ENUM_STRUCT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "StringInvalidForEnumStructType"));

            case ARRAY_INVALID_FOR_ENUM_STRUCT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ArrayInvalidForEnumStructType"));

            case VALUE_INVALID_FOR_ENUM_STRUCT_TYPE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "ValueInvalidForEnumStructType"));

            case INVALID_ENUM_VALUE ->
                Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "UnknownEnumValue"));

            case INVALID_TYPE -> Map.entry("error._InvalidInput", createInvalidField(e.fieldName, "InvalidType"));
        };
        return entry;
    }

    static Map<String, List<Map<String, String>>> createInvalidField(String field, String reason) {
        return createInvalidFields(Map.of(field, reason));
    }

    static Map<String, List<Map<String, String>>> createInvalidFields(Map<String, String> errors) {
        var jsonErrors = errors.entrySet().stream()
                .map(e -> (Map<String, String>) new TreeMap<>(Map.of("field", e.getKey(), "reason", e.getValue())))
                .collect(Collectors.toList());
        return Map.of("cases", jsonErrors);
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
}
