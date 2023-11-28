package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

class JApiSchemaTuple {
    public final Map<String, Object> original;
    public final Map<String, Type> parsed;

    public JApiSchemaTuple(Map<String, Object> original, Map<String, Type> parsed) {
        this.original = original;
        this.parsed = parsed;
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
}

class JsonBoolean implements Type {
}

class JsonInteger implements Type {
}

class JsonNumber implements Type {
}

class JsonString implements Type {
}

class JsonArray implements Type {
    public final TypeDeclaration nestedType;

    public JsonArray(TypeDeclaration nestedType) {
        this.nestedType = nestedType;
    }
}

class JsonObject implements Type {

    public final TypeDeclaration nestedType;

    public JsonObject(TypeDeclaration nestedType) {
        this.nestedType = nestedType;
    }
}

class JsonAny implements Type {
}

class Struct implements Type {

    public final String name;
    public final Map<String, FieldDeclaration> fields;

    public Struct(String name, Map<String, FieldDeclaration> fields) {
        this.name = name;
        this.fields = fields;
    }
}

class Enum implements Type {

    public final String name;
    public final Map<String, Struct> values;

    public Enum(String name, Map<String, Struct> values) {
        this.name = name;
        this.values = values;
    }
}

class Fn implements Type {

    public final String name;
    public final Struct arg;
    public final Enum result;

    public Fn(String name, Struct input, Enum output) {
        this.name = name;
        this.arg = input;
        this.result = output;
    }
}

class Trait implements Type {
    public final String name;
    public final Fn fn;
    public final String regex;

    public Trait(String name, Fn fn, String regex) {
        this.name = name;
        this.fn = fn;
        this.regex = regex;
    }
}

class Info implements Type {
    public final String name;

    public Info(String name) {
        this.name = name;
    }
}

class Ext implements Type {
    public final String name;
    public final TypeExtension typeExtension;

    public Ext(String name, TypeExtension typeExtension) {
        this.name = name;
        this.typeExtension = typeExtension;
    }
}

class MessageParseException extends Exception {
    public MessageParseException(Throwable cause) {
        super(cause);
    }
}

class BinaryEncoding {

    public final Map<String, Long> encodeMap;
    public final Map<Long, String> decodeMap;
    public final Integer checksum;

    public BinaryEncoding(Map<String, Long> binaryEncoding, Integer checksum) {
        this.encodeMap = binaryEncoding;
        this.decodeMap = binaryEncoding.entrySet().stream()
                .collect(Collectors.toMap(e -> Long.valueOf(e.getValue()), e -> e.getKey()));
        this.checksum = checksum;
    }
}

interface BinaryEncoder {
    List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError;

    List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError;
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

class Invocation {
    final String functionName;
    final Map<String, Object> functionArgument;
    boolean verified = false;

    public Invocation(String functionName, Map<String, Object> functionArgument) {
        this.functionName = functionName;
        this.functionArgument = functionArgument;
    }
}
