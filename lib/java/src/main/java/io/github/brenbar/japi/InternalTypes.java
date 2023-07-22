package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

class JApiSchema {
    public final Map<String, Object> original;
    public final Map<String, Definition> parsed;

    public JApiSchema(Map<String, Object> original, Map<String, Definition> parsed) {
        this.original = original;
        this.parsed = parsed;
    }
}

interface Definition {
    public String getName();
}

class TitleDefinition implements Definition {

    public final String name;

    public TitleDefinition(
            String name) {
        this.name = name;
    }

    @Override
    public String getName() {
        return name;
    }
}

class FunctionDefinition implements Definition {

    public final String name;
    public final Struct inputStruct;
    public final TypeDeclaration outputStruct;
    public final TypeDeclaration errorEnum;

    public FunctionDefinition(
            String name,
            Struct inputStruct,
            Struct outputStruct,
            Enum errorEnum) {
        this.name = name;
        this.inputStruct = inputStruct;
        this.outputStruct = new TypeDeclaration(outputStruct, false);
        this.errorEnum = new TypeDeclaration(errorEnum, false);
    }

    @Override
    public String getName() {
        return name;
    }
}

class TypeDefinition implements Definition {

    public final String name;
    public final Type type;

    public TypeDefinition(
            String name,
            Type type) {
        this.name = name;
        this.type = type;
    }

    @Override
    public String getName() {
        return name;
    }
}

class ErrorDefinition implements Definition {

    public final String name;
    public final Map<String, FieldDeclaration> fields;

    public ErrorDefinition(
            String name,
            Map<String, FieldDeclaration> fields) {
        this.name = name;
        this.fields = fields;
    }

    @Override
    public String getName() {
        return name;
    }
}

class FieldNameAndFieldDeclaration {

    public final String fieldName;
    public final FieldDeclaration fieldDeclaration;

    public FieldNameAndFieldDeclaration(
            String fieldName,
            FieldDeclaration fieldDeclaration) {
        this.fieldName = fieldName;
        this.fieldDeclaration = fieldDeclaration;
    }
}

class FieldDeclaration {

    public final TypeDeclaration typeDeclaration;
    public final boolean optional;

    public FieldDeclaration(
            TypeDeclaration typeDeclaration,
            boolean optional) {
        this.typeDeclaration = typeDeclaration;
        this.optional = optional;
    }
}

class TypeDeclaration {
    public final Type type;
    public final boolean nullable;

    public TypeDeclaration(
            Type type,
            boolean nullable) {
        this.type = type;
        this.nullable = nullable;
    }
}

interface Type {
    public String getName();
}

class JsonNull implements Type {
    @Override
    public String getName() {
        return "null";
    }
}

class JsonBoolean implements Type {
    @Override
    public String getName() {
        return "boolean";
    }
}

class JsonInteger implements Type {
    @Override
    public String getName() {
        return "integer";
    }
}

class JsonNumber implements Type {
    @Override
    public String getName() {
        return "number";
    }
}

class JsonString implements Type {
    @Override
    public String getName() {
        return "string";
    }
}

class JsonArray implements Type {
    public final TypeDeclaration nestedType;

    public JsonArray(TypeDeclaration nestedType) {
        this.nestedType = nestedType;
    }

    @Override
    public String getName() {
        return "array";
    }
}

class JsonObject implements Type {

    public final TypeDeclaration nestedType;

    public JsonObject(TypeDeclaration nestedType) {
        this.nestedType = nestedType;
    }

    @Override
    public String getName() {
        return "object";
    }
}

class JsonAny implements Type {
    @Override
    public String getName() {
        return "any";
    }
}

class Struct implements Type {

    public final String name;
    public final Map<String, FieldDeclaration> fields;

    public Struct(String name, Map<String, FieldDeclaration> fields) {
        this.name = name;
        this.fields = fields;
    }

    @Override
    public String getName() {
        return name;
    }
}

class Enum implements Type {

    public final String name;
    public final Map<String, Struct> values;

    public Enum(String name, Map<String, Struct> values) {
        this.name = name;
        this.values = values;
    }

    @Override
    public String getName() {
        return name;
    }
}

class BinaryEncoder {

    public final Map<String, Long> encodeMap;
    public final Map<Long, String> decodeMap;
    public final Long checksum;

    public BinaryEncoder(Map<String, Long> binaryEncoding, Long binaryHash) {
        this.encodeMap = binaryEncoding;
        this.decodeMap = binaryEncoding.entrySet().stream()
                .collect(Collectors.toMap(e -> Long.valueOf(e.getValue()), e -> e.getKey()));
        this.checksum = binaryHash;
    }
}

interface BinaryEncodingStrategy {
    List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError;

    List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError;
}

class Message {
    public final String target;
    public final Map<String, Object> headers;
    public final Map<String, Object> body;

    public Message(String target, Map<String, Object> headers, Map<String, Object> body) {
        this.target = target;
        this.headers = headers;
        this.body = body;
    }
}

class ValidationFailure {
    public final String path;
    public final String reason;

    public ValidationFailure(String path, String reason) {
        this.path = path;
        this.reason = reason;
    }
}

class ValidationErrorReasons {
    public static final String NULL_INVALID_FOR_NON_NULL_TYPE = "NullInvalidForNonNullType";

    public static final String NUMBER_INVALID_FOR_BOOLEAN_TYPE = "NumberInvalidForBooleanType";
    public static final String STRING_INVALID_FOR_BOOLEAN_TYPE = "StringInvalidForBooleanType";
    public static final String ARRAY_INVALID_FOR_BOOLEAN_TYPE = "ArrayInvalidForBooleanType";
    public static final String OBJECT_INVALID_FOR_BOOLEAN_TYPE = "ObjectInvalidForBooleanType";
    public static final String VALUE_INVALID_FOR_BOOLEAN_TYPE = "ValueInvalidForBooleanType";

    public static final String BOOLEAN_INVALID_FOR_INTEGER_TYPE = "BooleanInvalidForIntegerType";
    public static final String NUMBER_INVALID_FOR_INTEGER_TYPE = "NumberInvalidForIntegerType";
    public static final String STRING_INVALID_FOR_INTEGER_TYPE = "StringInvalidForIntegerType";
    public static final String ARRAY_INVALID_FOR_INTEGER_TYPE = "ArrayInvalidForIntegerType";
    public static final String OBJECT_INVALID_FOR_INTEGER_TYPE = "ObjectInvalidForIntegerType";
    public static final String VALUE_INVALID_FOR_INTEGER_TYPE = "ValueInvalidForIntegerType";

    public static final String BOOLEAN_INVALID_FOR_NUMBER_TYPE = "BooleanInvalidForNumberType";
    public static final String STRING_INVALID_FOR_NUMBER_TYPE = "StringInvalidForNumberType";
    public static final String ARRAY_INVALID_FOR_NUMBER_TYPE = "ArrayInvalidForNumberType";
    public static final String OBJECT_INVALID_FOR_NUMBER_TYPE = "ObjectInvalidForNumberType";
    public static final String VALUE_INVALID_FOR_NUMBER_TYPE = "ValueInvalidForNumberType";

    public static final String BOOLEAN_INVALID_FOR_STRING_TYPE = "BooleanInvalidForStringType";
    public static final String NUMBER_INVALID_FOR_STRING_TYPE = "NumberInvalidForStringType";
    public static final String ARRAY_INVALID_FOR_STRING_TYPE = "ArrayInvalidForStringType";
    public static final String OBJECT_INVALID_FOR_STRING_TYPE = "ObjectInvalidForStringType";
    public static final String VALUE_INVALID_FOR_STRING_TYPE = "ValueInvalidForStringType";

    public static final String BOOLEAN_INVALID_FOR_ARRAY_TYPE = "BooleanInvalidForArrayType";
    public static final String NUMBER_INVALID_FOR_ARRAY_TYPE = "NumberInvalidForArrayType";
    public static final String STRING_INVALID_FOR_ARRAY_TYPE = "StringInvalidForArrayType";
    public static final String OBJECT_INVALID_FOR_ARRAY_TYPE = "ObjectInvalidForArrayType";
    public static final String VALUE_INVALID_FOR_ARRAY_TYPE = "ValueInvalidForArrayType";

    public static final String BOOLEAN_INVALID_FOR_OBJECT_TYPE = "BooleanInvalidForObjectType";
    public static final String NUMBER_INVALID_FOR_OBJECT_TYPE = "NumberInvalidForObjectType";
    public static final String STRING_INVALID_FOR_OBJECT_TYPE = "StringInvalidForObjectType";
    public static final String ARRAY_INVALID_FOR_OBJECT_TYPE = "ArrayInvalidForObjectType";
    public static final String VALUE_INVALID_FOR_OBJECT_TYPE = "ValueInvalidForObjectType";

    public static final String BOOLEAN_INVALID_FOR_STRUCT_TYPE = "BooleanInvalidForStructType";
    public static final String NUMBER_INVALID_FOR_STRUCT_TYPE = "NumberInvalidForStructType";
    public static final String STRING_INVALID_FOR_STRUCT_TYPE = "StringInvalidForStructType";
    public static final String ARRAY_INVALID_FOR_STRUCT_TYPE = "ArrayInvalidForStructType";
    public static final String VALUE_INVALID_FOR_STRUCT_TYPE = "ValueInvalidForStructType";

    public static final String BOOLEAN_INVALID_FOR_ENUM_TYPE = "BooleanInvalidForEnumType";
    public static final String NUMBER_INVALID_FOR_ENUM_TYPE = "NumberInvalidForEnumType";
    public static final String STRING_INVALID_FOR_ENUM_TYPE = "StringInvalidForEnumType";
    public static final String ARRAY_INVALID_FOR_ENUM_TYPE = "ArrayInvalidForEnumType";
    public static final String VALUE_INVALID_FOR_ENUM_TYPE = "ValueInvalidForEnumType";

    public static final String BOOLEAN_INVALID_FOR_ENUM_STRUCT_TYPE = "BooleanInvalidForEnumStructType";
    public static final String NUMBER_INVALID_FOR_ENUM_STRUCT_TYPE = "NumberInvalidForEnumStructType";
    public static final String STRING_INVALID_FOR_ENUM_STRUCT_TYPE = "StringInvalidForEnumStructType";
    public static final String ARRAY_INVALID_FOR_ENUM_STRUCT_TYPE = "ArrayInvalidForEnumStructType";
    public static final String VALUE_INVALID_FOR_ENUM_STRUCT_TYPE = "ValueInvalidForEnumStructType";

    public static final String INVALID_ENUM_VALUE = "UnknownEnumValue";
    public static final String INVALID_TYPE = "InvalidType";

    public static final String REQUIRED_STRUCT_FIELD_MISSING = "RequiredStructFieldMissing";
    public static final String EXTRA_STRUCT_FIELD_NOT_ALLOWED = "UnknownStructField";

    public static final String MULTI_ENTRY_OBJECT_INVALID_FOR_ENUM_TYPE = "EnumDoesNotHaveExactlyOneField";
    public static final String UNKNOWN_ENUM_VALUE = "UnknownEnumField";

    public static final String NUMBER_OUT_OF_RANGE = "NumberOutOfRange";

    public static final String RESULT_ENUM_DOES_NOT_HAVE_EXACTLY_ONE_FIELD = "ResultEnumDoesNotHaveExactlyOneField";
    public static final String UNKNOWN_RESULT_ENUM_VALUE = "UnknownResultEnumField";
}

class Mock {
    final String whenFunctionName;
    final Map<String, Object> whenFunctionInput;
    final boolean exactMatchInput;
    final Function<Map<String, Object>, Map<String, Object>> thenAnswerOutput;

    public Mock(String whenFunctionName, Map<String, Object> whenFunctionInput, boolean exactMatchInput,
            Function<Map<String, Object>, Map<String, Object>> thenAnswerOutput) {
        this.whenFunctionName = whenFunctionName;
        this.whenFunctionInput = whenFunctionInput;
        this.exactMatchInput = exactMatchInput;
        this.thenAnswerOutput = thenAnswerOutput;
    }
}

class Invocation {
    final String functionName;
    final Map<String, Object> functionInput;
    boolean verified = false;

    public Invocation(String functionName, Map<String, Object> functionInput) {
        this.functionName = functionName;
        this.functionInput = functionInput;
    }
}
