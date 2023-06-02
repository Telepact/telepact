package io.github.brenbar.japi;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.msgpack.jackson.dataformat.MessagePackFactory;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.sql.Array;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import java.util.function.Supplier;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class Processor {
    interface Handler {
        Map<String, Object> handle(String functionName, Map<String, Object> headers, Map<String, Object> input);
    }

    private static class Error extends RuntimeException {
        public Error(String message) {
            super(message);
        }
        public Error(Throwable cause) {
            super(cause);
        }

        public Error() {
            super();
        }
    }

    private static class InvalidJson extends Error {
        public InvalidJson(Throwable cause) {
            super(cause);
        }
    }

    private static class JapiMessageArrayTooFewElements extends Error {}
    private static class JapiMessageNotArray extends Error {}
    private static class JapiMessageTypeNotString extends Error {}
    private static class JapiMessageTypeNotFunction extends Error {}
    private static class JapiMessageHeaderNotObject extends Error {}
    private static class InvalidBinaryEncoding extends Error {}
    private static class BinaryDecodeFailure extends Error {
        public BinaryDecodeFailure(Throwable cause) {
            super(cause);
        }
    }
    private static class JapiMessageBodyNotObject extends Error {}
    private static class FunctionNotFound extends Error {
        public final String functionName;
        public FunctionNotFound(String functionName) {
            super("Function not found: %s".formatted(functionName));
            this.functionName = functionName;
        }
    }
    private static class InvalidInput extends Error {}
    private static class InvalidOutput extends Error {
        public InvalidOutput(Throwable cause) {
            super(cause);
        }
    }
    private static class FieldError extends InvalidInput {
    }

    private static class StructMissingFields extends FieldError {
        public final String namespace;
        public final List<String> missingFields;
        public StructMissingFields(String namespace, List<String> missingFields) {
            super();
            this.namespace = namespace;
            this.missingFields = missingFields;
        }
    }

    private static class StructHasExtraFields extends FieldError {
        public final String namespace;
        public final List<String> extraFields;
        public StructHasExtraFields(String namespace, List<String> extraFields) {
            super();
            this.namespace = namespace;
            this.extraFields = extraFields;
        }
    }

    private static class UnionDoesNotHaveOnlyOneField extends FieldError {
        public final String namespace;
        public UnionDoesNotHaveOnlyOneField(String namespace) {
            super();
            this.namespace = namespace;
        }
    }

    private static class UnknownUnionField extends FieldError {
        public final String namespace;
        public final String field;
        public UnknownUnionField(String namespace, String field) {
            super();
            this.namespace = namespace;
            this.field = field;
        }
    }

    private static class InvalidFieldType extends FieldError {
        public final String fieldName;
        public final InvalidFieldTypeError error;
        public InvalidFieldType(String fieldName, InvalidFieldTypeError error) {
            this.fieldName = fieldName;
            this.error = error;
        }
    }

    public enum InvalidFieldTypeError {
        NULL_INVALID_FOR_NON_NULL_TYPE,

        NUMBER_INVALID_FOR_BOOLEAN_TYPE,
        STRING_INVALID_FOR_BOOLEAN_TYPE,
        ARRAY_INVALID_FOR_BOOLEAN_TYPE,
        OBJECT_INVALID_FOR_BOOLEAN_TYPE,
        VALUE_INVALID_FOR_BOOLEAN_TYPE,

        BOOLEAN_INVALID_FOR_INTEGER_TYPE,
        NUMBER_INVALID_FOR_INTEGER_TYPE,
        STRING_INVALID_FOR_INTEGER_TYPE,
        ARRAY_INVALID_FOR_INTEGER_TYPE,
        OBJECT_INVALID_FOR_INTEGER_TYPE,
        VALUE_INVALID_FOR_INTEGER_TYPE,

        BOOLEAN_INVALID_FOR_NUMBER_TYPE,
        STRING_INVALID_FOR_NUMBER_TYPE,
        ARRAY_INVALID_FOR_NUMBER_TYPE,
        OBJECT_INVALID_FOR_NUMBER_TYPE,
        VALUE_INVALID_FOR_NUMBER_TYPE,

        BOOLEAN_INVALID_FOR_STRING_TYPE,
        NUMBER_INVALID_FOR_STRING_TYPE,
        ARRAY_INVALID_FOR_STRING_TYPE,
        OBJECT_INVALID_FOR_STRING_TYPE,
        VALUE_INVALID_FOR_STRING_TYPE,

        BOOLEAN_INVALID_FOR_ARRAY_TYPE,
        NUMBER_INVALID_FOR_ARRAY_TYPE,
        STRING_INVALID_FOR_ARRAY_TYPE,
        OBJECT_INVALID_FOR_ARRAY_TYPE,
        VALUE_INVALID_FOR_ARRAY_TYPE,

        BOOLEAN_INVALID_FOR_OBJECT_TYPE,
        NUMBER_INVALID_FOR_OBJECT_TYPE,
        STRING_INVALID_FOR_OBJECT_TYPE,
        ARRAY_INVALID_FOR_OBJECT_TYPE,
        VALUE_INVALID_FOR_OBJECT_TYPE,

        BOOLEAN_INVALID_FOR_STRUCT_TYPE,
        NUMBER_INVALID_FOR_STRUCT_TYPE,
        STRING_INVALID_FOR_STRUCT_TYPE,
        ARRAY_INVALID_FOR_STRUCT_TYPE,
        VALUE_INVALID_FOR_STRUCT_TYPE,

        BOOLEAN_INVALID_FOR_UNION_TYPE,
        NUMBER_INVALID_FOR_UNION_TYPE,
        STRING_INVALID_FOR_UNION_TYPE,
        ARRAY_INVALID_FOR_UNION_TYPE,
        VALUE_INVALID_FOR_UNION_TYPE,

        BOOLEAN_INVALID_FOR_ENUM_TYPE,
        NUMBER_INVALID_FOR_ENUM_TYPE,
        ARRAY_INVALID_FOR_ENUM_TYPE,
        OBJECT_INVALID_FOR_ENUM_TYPE,
        VALUE_INVALID_FOR_ENUM_TYPE,

        INVALID_ENUM_VALUE,
    }

    private Handler handler;
    private Handler internalHandler;
    private Map<String, Object> originalApiDescription;
    private Map<String, Parser.Definition> apiDescription;
    private Consumer<Throwable> onError;

    private Map<String, Integer> binaryEncoding;
    private Map<Integer, String> binaryEncodingReversed;
    private long binaryHash;

    public Processor(Handler handler, String apiDescriptionJson) {
        this(handler, apiDescriptionJson, (e) -> {});
    }

    public Processor(Handler handler, String apiDescriptionJson, Consumer<Throwable> onError) {
        var description = Parser.newJapiDescription(apiDescriptionJson);
        // Also add the internal api spec
        this.apiDescription = description.parsed();
        this.originalApiDescription = description.original();

        var internalDescription = Parser.newJapiDescription("""
        {
          "function._ping": [
            {},
            {}
          ],
          "function._api": [
            {},
            {
              "api": "object"
            }
          ]
        }
        """);

        this.apiDescription.putAll(internalDescription.parsed());
        this.originalApiDescription.putAll(internalDescription.original());

        this.handler = handler;
        this.internalHandler = (functionName, headers, input) -> switch (functionName) {
            case "_ping" -> Map.of();
            case "_api" -> Map.of("api", originalApiDescription);
            default -> throw new FunctionNotFound(functionName);
        };
        this.onError = onError;

        // Calculate binary hash
        var allApiDescriptionKeys = new TreeSet<String>();
        for (var entry : apiDescription.entrySet()) {
            allApiDescriptionKeys.add(entry.getKey());
            if (entry.getValue() instanceof Parser.FunctionDefinition f) {
                allApiDescriptionKeys.addAll(f.inputFields().keySet());
                allApiDescriptionKeys.addAll(f.outputFields().keySet());
                allApiDescriptionKeys.addAll(f.errors());
            } else if (entry.getValue() instanceof Parser.TypeDefinition t) {
                var type = t.type();
                if (type instanceof Parser.Struct o) {
                    allApiDescriptionKeys.addAll(o.fields().keySet());
                } else if (type instanceof Parser.Union u) {
                    allApiDescriptionKeys.addAll(u.cases().keySet());
                } else if (type instanceof Parser.Enum e) {
                    allApiDescriptionKeys.addAll(e.allowedValues());
                }
            }
        }
        var atomicInteger = new AtomicInteger(0);
        this.binaryEncoding = allApiDescriptionKeys.stream().collect(Collectors.toMap(k -> k, k -> atomicInteger.getAndIncrement()));
        this.binaryEncodingReversed = this.binaryEncoding.entrySet().stream().collect(Collectors.toMap(e -> e.getValue(), e -> e.getKey()));
        var finalString = allApiDescriptionKeys.stream().collect(Collectors.joining("\n"));
        try {
            var hash = MessageDigest.getInstance("SHA-256").digest(finalString.getBytes(StandardCharsets.UTF_8));
            var buffer = ByteBuffer.wrap(hash);
            this.binaryHash = buffer.getLong();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    private void gatherAllApiDescriptionKeys(HashSet<String> allKeys, Map<String, Object> node) {
        for (var entry : node.entrySet()) {
            allKeys.add(entry.getKey());
            if (entry.getValue() instanceof Map<?,?> m) {
                gatherAllApiDescriptionKeys(allKeys, node);
            }
        }
    }

    public byte[] process(byte[] inputJson) {
        var objectMapper = new ObjectMapper();
        JsonNode inputJsonNode;
        boolean isMessagePack = false;
        try {
            inputJsonNode = objectMapper.readTree(inputJson);
        } catch (IOException e) {
            // Try msgpack
            var msgPackMapper = new ObjectMapper(new MessagePackFactory());
            try {
                inputJsonNode = msgPackMapper.readTree(inputJson);
                isMessagePack = true;
            } catch (IOException ex) {
                throw new InvalidJson(ex);
            }
        }

        List<Object> inputJsonJava;
        try {
            inputJsonJava = objectMapper.convertValue(inputJsonNode, new TypeReference<List<Object>>() {});
        } catch (IllegalArgumentException e) {
            throw new JapiMessageNotArray();
        }

        var outputJsonJava = process(inputJsonJava, isMessagePack);

        try {
            return objectMapper.writeValueAsBytes(outputJsonJava);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }

    public List<Object> process(List<Object> inputJsonJava, boolean inputIsMessagepack) {
        var finalHeaders = new HashMap<String, Object>();
        try {
            try {
                if (inputJsonJava.size() < 3) {
                    throw new JapiMessageArrayTooFewElements();
                }

                String messageType;
                if (!inputIsMessagepack) {
                    try {
                        messageType = (String) inputJsonJava.get(0);
                    } catch (ClassCastException e) {
                        throw new JapiMessageTypeNotString();
                    }
                } else {
                    try {
                        var encodedMessageType = (Integer) inputJsonJava.get(0);
                        messageType = binaryEncodingReversed.get(encodedMessageType);
                    } catch (Exception e) {
                        throw new BinaryDecodeFailure(e);
                    }
                }

                var regex = Pattern.compile("^function\\.([a-zA-Z_][a-zA-Z0-9_]*)(.input)?");
                var matcher = regex.matcher(messageType);
                if (!matcher.matches()) {
                    throw new JapiMessageTypeNotFunction();
                }
                var functionName = matcher.group(1);

                Map<String, Object> headers;
                try {
                    headers = (Map<String, Object>) inputJsonJava.get(1);
                } catch (ClassCastException e) {
                    throw new JapiMessageHeaderNotObject();
                }

                var returnAsBinary = false;

                if (inputIsMessagepack) {
                    var givenHash = (Long) headers.get("_bin");
                    if (givenHash != binaryHash) {
                        throw new InvalidBinaryEncoding();
                    }

                    finalHeaders.put("_bin", this.binaryHash);
                    returnAsBinary = true;
                }


                if (headers.containsKey("_binaryStart")) {
                    // Client is initiating handshake for binary protocol
                    finalHeaders.put("_bin", this.binaryHash);
                    finalHeaders.put("_binaryEncoding", this.binaryEncoding);
                    returnAsBinary = true;
                }

                // Reflect call id
                var callId = headers.get("_id");
                if (callId != null) {
                    finalHeaders.put("_id", callId);
                }

                Map<String, Object> messageBody;
                if (!inputIsMessagepack) {
                    try {
                        messageBody = (Map<String, Object>) inputJsonJava.get(2);
                    } catch (ClassCastException e) {
                        throw new JapiMessageBodyNotObject();
                    }
                } else {
                    // Need to decode the data
                    Map<Integer, Object> initialMessageBody;
                    try {
                        initialMessageBody = (Map<Integer, Object>) inputJsonJava.get(2);
                    } catch (ClassCastException e) {
                        throw new JapiMessageBodyNotObject();
                    }

                    try {
                        messageBody = (Map<String, Object>) decode(initialMessageBody);
                    } catch (Exception e) {
                        throw new BinaryDecodeFailure(e);
                    }
                }

                var output = _process(functionName, headers, messageBody);

                var outputMessageType = "function.%s.output".formatted(functionName);

                Object finalOutput;
                Object finalOutputMessageType;
                if (returnAsBinary) {
                    finalOutput = encode(finalHeaders);
                    finalOutputMessageType = binaryEncoding.get(outputMessageType);
                } else {
                    finalOutput = output;
                    finalOutputMessageType = outputMessageType;
                }

                return List.of(finalOutputMessageType, finalHeaders, finalOutput);
            } catch (Exception e) {
                try {
                    this.onError.accept(e);
                } catch (Exception ignored) {}
                throw e;
            }
        } catch (StructHasExtraFields e) {
            var messageType = "error._InvalidInput";
            var errors = e.extraFields.stream().collect(Collectors.toMap(f -> "%s.%s".formatted(e.namespace, f), f -> "UnknownStructField"));
            var messageBody = invalidFields(errors);

            return List.of(messageType, finalHeaders, messageBody);

        } catch (StructMissingFields e) {
            var messageType = "error._InvalidInput";
            var errors = e.missingFields.stream().collect(Collectors.toMap(f -> "%s.%s".formatted(e.namespace, f), f -> "RequiredStructFieldMissing"));
            var messageBody = invalidFields(errors);

            return List.of(messageType, finalHeaders, messageBody);

        } catch (UnknownUnionField e) {
            var messageType = "error._InvalidInput";
            var messageBody = invalidField("%s.%s".formatted(e.namespace, e.field), "UnknownUnionField");

            return List.of(messageType, finalHeaders, messageBody);
        } catch (UnionDoesNotHaveOnlyOneField e) {
            var messageType = "error._InvalidInput";
            var messageBody = invalidField(e.namespace, "UnionDoesNotHaveExactlyOneField");

            return List.of(messageType, finalHeaders, messageBody);
        } catch (InvalidFieldType e) {
            var entry = switch (e.error) {
                case NULL_INVALID_FOR_NON_NULL_TYPE ->
                        Map.entry("error._InvalidInput", invalidField(e.fieldName, "NullInvalidForNonNullType"));

                case NUMBER_INVALID_FOR_BOOLEAN_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "NumberInvalidForBooleanType"));

                case STRING_INVALID_FOR_BOOLEAN_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "StringInvalidForBooleanType"));

                case ARRAY_INVALID_FOR_BOOLEAN_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ArrayInvalidForBooleanType"));

                case OBJECT_INVALID_FOR_BOOLEAN_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ObjectInvalidForBooleanType"));

                case VALUE_INVALID_FOR_BOOLEAN_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ValueInvalidForBooleanType"));

                case BOOLEAN_INVALID_FOR_INTEGER_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "BooleanInvalidForIntegerType"));

                case NUMBER_INVALID_FOR_INTEGER_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "NumberInvalidForIntegerType"));

                case STRING_INVALID_FOR_INTEGER_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "StringInvalidForIntegerType"));

                case ARRAY_INVALID_FOR_INTEGER_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ArrayInvalidForIntegerType"));

                case OBJECT_INVALID_FOR_INTEGER_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ObjectInvalidForIntegerType"));

                case VALUE_INVALID_FOR_INTEGER_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ValueInvalidForIntegerType"));

                case BOOLEAN_INVALID_FOR_NUMBER_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "BooleanInvalidForNumberType"));

                case STRING_INVALID_FOR_NUMBER_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "StringInvalidForNumberType"));

                case ARRAY_INVALID_FOR_NUMBER_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ArrayInvalidForNumberType"));

                case OBJECT_INVALID_FOR_NUMBER_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ObjectInvalidForNumberType"));

                case VALUE_INVALID_FOR_NUMBER_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ValueInvalidForNumberType"));

                case BOOLEAN_INVALID_FOR_STRING_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "BooleanInvalidForStringType"));

                case NUMBER_INVALID_FOR_STRING_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "NumberInvalidForStringType"));

                case ARRAY_INVALID_FOR_STRING_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ArrayInvalidForStringType"));

                case OBJECT_INVALID_FOR_STRING_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ObjectInvalidForStringType"));

                case VALUE_INVALID_FOR_STRING_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ValueInvalidForStringType"));

                case BOOLEAN_INVALID_FOR_ARRAY_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "BooleanInvalidForArrayType"));

                case NUMBER_INVALID_FOR_ARRAY_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "NumberInvalidForArrayType"));

                case STRING_INVALID_FOR_ARRAY_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "StringInvalidForArrayType"));

                case OBJECT_INVALID_FOR_ARRAY_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ObjectInvalidForArrayType"));

                case VALUE_INVALID_FOR_ARRAY_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ValueInvalidForArrayType"));

                case BOOLEAN_INVALID_FOR_OBJECT_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "BooleanInvalidForObjectType"));

                case NUMBER_INVALID_FOR_OBJECT_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "NumberInvalidForObjectType"));

                case STRING_INVALID_FOR_OBJECT_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "StringInvalidForObjectType"));

                case ARRAY_INVALID_FOR_OBJECT_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ArrayInvalidForObjectType"));

                case VALUE_INVALID_FOR_OBJECT_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ValueInvalidForObjectType"));

                case BOOLEAN_INVALID_FOR_STRUCT_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "BooleanInvalidForStructType"));

                case NUMBER_INVALID_FOR_STRUCT_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "NumberInvalidForStructType"));

                case STRING_INVALID_FOR_STRUCT_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "StringInvalidForStructType"));

                case ARRAY_INVALID_FOR_STRUCT_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ArrayInvalidForStructType"));

                case VALUE_INVALID_FOR_STRUCT_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ValueInvalidForStructType"));

                case BOOLEAN_INVALID_FOR_UNION_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "BooleanInvalidForUnionType"));

                case NUMBER_INVALID_FOR_UNION_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "NumberInvalidForUnionType"));

                case STRING_INVALID_FOR_UNION_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "StringInvalidForUnionType"));

                case ARRAY_INVALID_FOR_UNION_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ArrayInvalidForUnionType"));

                case VALUE_INVALID_FOR_UNION_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ValueInvalidForUnionType"));

                case BOOLEAN_INVALID_FOR_ENUM_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "BooleanInvalidForEnumType"));

                case NUMBER_INVALID_FOR_ENUM_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "NumberInvalidForEnumType"));

                case ARRAY_INVALID_FOR_ENUM_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ArrayInvalidForEnumType"));

                case OBJECT_INVALID_FOR_ENUM_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ObjectInvalidForEnumType"));

                case VALUE_INVALID_FOR_ENUM_TYPE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "ValueInvalidForEnumType"));

                case INVALID_ENUM_VALUE -> Map.entry("error._InvalidInput", invalidField(e.fieldName, "UnknownEnumValue"));

            };

            var messageType = entry.getKey();
            var messageBody = entry.getValue();

            return List.of(messageType, finalHeaders, messageBody);
        } catch (InvalidOutput e) {
            var messageType = "error._InvalidOutput";

            return List.of(messageType, finalHeaders, Map.of());
        } catch (InvalidInput e) {
            var messageType = "error._InvalidInput";

            return List.of(messageType, finalHeaders, Map.of());
        } catch (InvalidBinaryEncoding | BinaryDecodeFailure e) {
            var messageType = "error._InvalidBinary";

            finalHeaders.put("_binaryEncoding", binaryEncoding);

            return List.of(messageType, finalHeaders, Map.of());

        } catch (Exception e) {
            var messageType = "error._ApplicationFailure";

            return List.of(messageType, finalHeaders, Map.of());
        }

    }

    private Map<String, List<Map<String, String>>> invalidField(String field, String reason) {
        return invalidFields(Map.of(field, reason));
    }

    private Map<String, List<Map<String, String>>> invalidFields(Map<String, String> errors) {
        var jsonErrors = errors.entrySet().stream().map(e -> (Map<String, String>) new TreeMap<>(Map.of("field", e.getKey(), "reason", e.getValue()))).collect(Collectors.toList());
        return Map.of("cases", jsonErrors);
    }

    private Object decode(Object given) {
        if (given instanceof Map<?,?> m) {
            return m.entrySet().stream().collect(Collectors.toMap(e -> this.binaryEncodingReversed.get(e.getKey()), e -> decode(e.getValue())));
        } else if (given instanceof List<?> l) {
            return l.stream().map(e -> decode(e));
        } else {
            return given;
        }
    }

    private Object encode(Object given) {
        if (given instanceof Map<?,?> m) {
            return m.entrySet().stream().collect(Collectors.toMap(e -> this.binaryEncoding.get(e.getKey()), e -> encode(e.getValue())));
        } else if (given instanceof List<?> l) {
            return l.stream().map(e -> encode(e));
        } else {
            return given;
        }
    }

    private Map<String, Object> _process(String functionName, Map<String, Object> headers, Map<String, Object> input) {
        var messageType = "function.%s".formatted(functionName);
        var functionDef = this.apiDescription.get(messageType);

        Map<String, Parser.FieldDeclaration> inputDefinition;
        Map<String, Parser.FieldDeclaration> outputDefinition;
        if (functionDef instanceof Parser.FunctionDefinition f) {
            inputDefinition = f.inputFields();
            outputDefinition = f.outputFields();
        } else {
            throw new FunctionNotFound(functionName);
        }

        validateStruct("input", inputDefinition, input);

        Map<String, Object> output;
        if (functionName.startsWith("_")) {
            output = internalHandler.handle(functionName, headers, input);
        } else {
            output = handler.handle(functionName, headers, input);
        }

        try {
            validateStruct("output", outputDefinition, output);
        } catch (Exception e) {
            throw new InvalidOutput(e);
        }

        return output;
    }

    private void validateStruct(
            String namespace,
            Map<String, Parser.FieldDeclaration> referenceStruct,
            Map<String, Object> actualStruct
    ) {
        var missingFields = new ArrayList<String>();
        for (Map.Entry<String, Parser.FieldDeclaration> entry : referenceStruct.entrySet()) {
            var name = entry.getKey();
            var fieldDeclaration = entry.getValue();
            if (!actualStruct.containsKey(name) && !fieldDeclaration.optional()) {
                missingFields.add(name);
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
            var name = entry.getKey();
            var field = entry.getValue();
            var referenceField = referenceStruct.get(name);
            if (referenceField == null) {
                throw new StructHasExtraFields(namespace, List.of(name));
            }
            validateType("%s.%s".formatted(namespace, name), referenceField.typeDeclaration(), field);
        }
    }

    private void validateUnion(
            String namespace,
            Map<String, Parser.FieldDeclaration> referenceStruct,
            Map<String, Object> actualStruct
    ) {
        if (actualStruct.size() != 1) {
            throw new UnionDoesNotHaveOnlyOneField(namespace);
        }

        var entry = actualStruct.entrySet().stream().findFirst().get();
        var name = entry.getKey();
        var fieldValue = entry.getValue();

        var referenceField = referenceStruct.get(name);
        if (referenceField == null) {
            throw new UnknownUnionField(namespace, name);
        }

        validateType("%s.%s".formatted(namespace, name), referenceField.typeDeclaration(), fieldValue);
    }

    private void validateType(String fieldName, Parser.TypeDeclaration typeDeclaration, Object value) {
        if (value == null) {
            if (!typeDeclaration.nullable()) {
                throw new InvalidFieldType(fieldName, InvalidFieldTypeError.NULL_INVALID_FOR_NON_NULL_TYPE);
            } else {
                return;
            }
        } else {
            var expectedType = typeDeclaration.type();
            if (expectedType instanceof Parser.JsonBoolean) {
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
            } else if (expectedType instanceof Parser.JsonInteger) {
                if (value instanceof Boolean) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_INTEGER_TYPE);
                } else if (value instanceof Number) {
                    if (value instanceof Long || value instanceof Integer) {
                        return;
                    } else {
                        throw new InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_INTEGER_TYPE);
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
            } else if (expectedType instanceof Parser.JsonNumber) {
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
            } else if (expectedType instanceof Parser.JsonString) {
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
            } else if (expectedType instanceof Parser.JsonArray a) {
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
            } else if (expectedType instanceof Parser.JsonObject o) {
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
            } else if (expectedType instanceof Parser.Struct s) {
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
            } else if (expectedType instanceof Parser.Union u) {
                if (value instanceof Boolean) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_UNION_TYPE);
                } else if (value instanceof Number) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_UNION_TYPE);
                } else if (value instanceof String) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_UNION_TYPE);
                } else if (value instanceof List) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_UNION_TYPE);
                } else if (value instanceof Map<?, ?> m) {
                    validateUnion(fieldName, u.cases(), (Map<String, Object>) m);
                    return;
                } else {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_UNION_TYPE);
                }
            } else if (expectedType instanceof Parser.Enum e) {
                if (value instanceof Boolean) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ENUM_TYPE);
                } else if (value instanceof Number) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_ENUM_TYPE);
                } else if (value instanceof String s) {
                    if (!e.allowedValues().contains(s)) {
                        throw new InvalidFieldType(fieldName, InvalidFieldTypeError.INVALID_ENUM_VALUE);
                    } else {
                        return;
                    }
                } else if (value instanceof List) {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_ENUM_TYPE);
                } else if (value instanceof Map<?, ?>) {
                    // TODO: Allow single member maps to pass in enum value as member key and coerce here to string
                    // which will allow for a more efficient binary encoding
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_ENUM_TYPE);
                } else {
                    throw new InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_ENUM_TYPE);
                }
            }

        }
    }
}
