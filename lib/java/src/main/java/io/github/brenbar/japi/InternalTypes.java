package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;

interface Type {
    public String getName();
}

interface Definition {
    public String getName();
}

record Japi(Map<String, Object> original, Map<String, Definition> parsed) {
}

class JsonAny implements Type {
    @Override
    public String getName() {
        return "any";
    }
}

record JsonArray(TypeDeclaration nestedType) implements Type {
    @Override
    public String getName() {
        return "array";
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

class JsonNull implements Type {
    @Override
    public String getName() {
        return "null";
    }
}

class JsonNumber implements Type {
    @Override
    public String getName() {
        return "number";
    }
}

record JsonObject(TypeDeclaration nestedType) implements Type {
    @Override
    public String getName() {
        return "object";
    }
}

class JsonString implements Type {
    @Override
    public String getName() {
        return "string";
    }
}

record Struct(String name, Map<String, FieldDeclaration> fields) implements Type {
    @Override
    public String getName() {
        return name;
    }
}

record Enum(String name, Map<String, Struct> cases) implements Type {
    @Override
    public String getName() {
        return name;
    }
}

record ErrorDefinition(
        String name,
        Map<String, FieldDeclaration> fields) implements Definition {
    @Override
    public String getName() {
        return name;
    }
}

record FunctionDefinition(
        String name,
        Struct inputStruct,
        Struct outputStruct,
        List<String> errors) implements Definition {
    @Override
    public String getName() {
        return name;
    }
}

record FieldDeclaration(
        TypeDeclaration typeDeclaration,
        boolean optional) {
}

record FieldNameAndFieldDeclaration(
        String fieldName,
        FieldDeclaration fieldDeclaration) {
}

record TitleDefinition(
        String name) implements Definition {
    @Override
    public String getName() {
        return name;
    }
}

record TypeDefinition(
        String name,
        Type type) implements Definition {
    @Override
    public String getName() {
        return name;
    }
}

record TypeDeclaration(
        Type type,
        boolean nullable) {
}

class JapiMessageArrayTooFewElements extends RuntimeException {
}

class JapiMessageTypeNotString extends RuntimeException {
}

class JapiMessageNotArray extends RuntimeException {
}

class JapiMessageTypeNotFunction extends RuntimeException {
}

class JapiMessageHeaderNotObject extends RuntimeException {
}

class InvalidBinaryEncoding extends RuntimeException {
}

class InvalidSelectFieldsHeader extends RuntimeException {
}

class BinaryDecodeFailure extends RuntimeException {
    public BinaryDecodeFailure(Throwable cause) {
        super(cause);
    }
}

class JapiMessageBodyNotObject extends RuntimeException {
}

class FunctionNotFound extends RuntimeException {
    public final String functionName;

    public FunctionNotFound(String functionName) {
        super("Function not found: %s".formatted(functionName));
        this.functionName = functionName;
    }
}

class InvalidInput extends RuntimeException {
    public InvalidInput() {
        super();
    }

    public InvalidInput(Throwable cause) {
        super(cause);
    }

}

class InvalidOutput extends RuntimeException {
    public InvalidOutput(Throwable cause) {
        super(cause);
    }
}

class InvalidApplicationFailure extends RuntimeException {
    public InvalidApplicationFailure(Throwable cause) {
        super(cause);
    }
}

class DisallowedError extends RuntimeException {
    public DisallowedError(Throwable cause) {
        super(cause);
    }
}

class FieldError extends InvalidInput {
    public FieldError() {
        super();
    }

    public FieldError(Throwable cause) {
        super(cause);
    }
}

class StructMissingFields extends FieldError {
    public final String namespace;
    public final List<String> missingFields;

    public StructMissingFields(String namespace, List<String> missingFields) {
        super();
        this.namespace = namespace;
        this.missingFields = missingFields;
    }
}

class StructHasExtraFields extends FieldError {
    public final String namespace;
    public final List<String> extraFields;

    public StructHasExtraFields(String namespace, List<String> extraFields) {
        super();
        this.namespace = namespace;
        this.extraFields = extraFields;
    }
}

class EnumDoesNotHaveOnlyOneField extends FieldError {
    public final String namespace;

    public EnumDoesNotHaveOnlyOneField(String namespace) {
        super();
        this.namespace = namespace;
    }
}

class UnknownEnumField extends FieldError {
    public final String namespace;
    public final String field;

    public UnknownEnumField(String namespace, String field) {
        super();
        this.namespace = namespace;
        this.field = field;
    }
}

class InvalidFieldType extends FieldError {
    public final String fieldName;
    public final String error;

    public InvalidFieldType(String fieldName, String error) {
        this.fieldName = fieldName;
        this.error = error;
    }

    public InvalidFieldType(String fieldName, String error, Throwable cause) {
        super(cause);
        this.fieldName = fieldName;
        this.error = error;
    }
}

class JapiMessageParseError extends RuntimeException {
    public String target;

    public JapiMessageParseError(String target) {
        this.target = target;
    }
}

class BinaryChecksumMismatchException extends Exception {
}

class InvalidFieldTypeError {
    public static final String NULL_INVALID_FOR_NON_NULL_TYPE = "NullInvalidForNonNullType";

    public static final String NUMBER_INVALID_FOR_BOOLEAN_TYPE = "NumberInvalidForBooleanType";
    public static final String STRING_INVALID_FOR_BOOLEAN_TYPE = "StringInvalidForBooleanType";
    public static final String ARRAY_INVALID_FOR_BOOLEAN_TYPE = "StringInvalidForBooleanType";
    public static final String OBJECT_INVALID_FOR_BOOLEAN_TYPE = "StringInvalidForBooleanType";
    public static final String VALUE_INVALID_FOR_BOOLEAN_TYPE = "StringInvalidForBooleanType";

    public static final String BOOLEAN_INVALID_FOR_INTEGER_TYPE = "StringInvalidForIntegerType";
    public static final String NUMBER_INVALID_FOR_INTEGER_TYPE = "StringInvalidForIntegerType";
    public static final String STRING_INVALID_FOR_INTEGER_TYPE = "StringInvalidForIntegerType";
    public static final String ARRAY_INVALID_FOR_INTEGER_TYPE = "StringInvalidForIntegerType";
    public static final String OBJECT_INVALID_FOR_INTEGER_TYPE = "StringInvalidForIntegerType";
    public static final String VALUE_INVALID_FOR_INTEGER_TYPE = "StringInvalidForIntegerType";

    public static final String BOOLEAN_INVALID_FOR_NUMBER_TYPE = "StringInvalidForNumberType";
    public static final String STRING_INVALID_FOR_NUMBER_TYPE = "StringInvalidForNumberType";
    public static final String ARRAY_INVALID_FOR_NUMBER_TYPE = "StringInvalidForNumberType";
    public static final String OBJECT_INVALID_FOR_NUMBER_TYPE = "StringInvalidForNumberType";
    public static final String VALUE_INVALID_FOR_NUMBER_TYPE = "StringInvalidForNumberType";

    public static final String BOOLEAN_INVALID_FOR_STRING_TYPE = "StringInvalidForStringType";
    public static final String NUMBER_INVALID_FOR_STRING_TYPE = "StringInvalidForStringType";
    public static final String ARRAY_INVALID_FOR_STRING_TYPE = "StringInvalidForStringType";
    public static final String OBJECT_INVALID_FOR_STRING_TYPE = "StringInvalidForStringType";
    public static final String VALUE_INVALID_FOR_STRING_TYPE = "StringInvalidForStringType";

    public static final String BOOLEAN_INVALID_FOR_ARRAY_TYPE = "StringInvalidForArrayType";
    public static final String NUMBER_INVALID_FOR_ARRAY_TYPE = "StringInvalidForArrayType";
    public static final String STRING_INVALID_FOR_ARRAY_TYPE = "StringInvalidForArrayType";
    public static final String OBJECT_INVALID_FOR_ARRAY_TYPE = "StringInvalidForArrayType";
    public static final String VALUE_INVALID_FOR_ARRAY_TYPE = "StringInvalidForArrayType";

    public static final String BOOLEAN_INVALID_FOR_OBJECT_TYPE = "StringInvalidForObjectType";
    public static final String NUMBER_INVALID_FOR_OBJECT_TYPE = "StringInvalidForObjectType";
    public static final String STRING_INVALID_FOR_OBJECT_TYPE = "StringInvalidForObjectType";
    public static final String ARRAY_INVALID_FOR_OBJECT_TYPE = "StringInvalidForObjectType";
    public static final String VALUE_INVALID_FOR_OBJECT_TYPE = "StringInvalidForObjectType";

    public static final String BOOLEAN_INVALID_FOR_STRUCT_TYPE = "StringInvalidForStructType";
    public static final String NUMBER_INVALID_FOR_STRUCT_TYPE = "StringInvalidForStructType";
    public static final String STRING_INVALID_FOR_STRUCT_TYPE = "StringInvalidForStructType";
    public static final String ARRAY_INVALID_FOR_STRUCT_TYPE = "StringInvalidForStructType";
    public static final String VALUE_INVALID_FOR_STRUCT_TYPE = "StringInvalidForStructType";

    public static final String BOOLEAN_INVALID_FOR_ENUM_TYPE = "StringInvalidForEnumType";
    public static final String NUMBER_INVALID_FOR_ENUM_TYPE = "StringInvalidForEnumType";
    public static final String STRING_INVALID_FOR_ENUM_TYPE = "StringInvalidForEnumType";
    public static final String ARRAY_INVALID_FOR_ENUM_TYPE = "StringInvalidForEnumType";
    public static final String VALUE_INVALID_FOR_ENUM_TYPE = "StringInvalidForEnumType";

    public static final String BOOLEAN_INVALID_FOR_ENUM_STRUCT_TYPE = "StringInvalidForEnumStructType";
    public static final String NUMBER_INVALID_FOR_ENUM_STRUCT_TYPE = "StringInvalidForEnumStructType";
    public static final String STRING_INVALID_FOR_ENUM_STRUCT_TYPE = "StringInvalidForEnumStructType";
    public static final String ARRAY_INVALID_FOR_ENUM_STRUCT_TYPE = "StringInvalidForEnumStructType";
    public static final String VALUE_INVALID_FOR_ENUM_STRUCT_TYPE = "StringInvalidForEnumStructType";

    public static final String INVALID_ENUM_VALUE = "UnknownEnumValue";
    public static final String INVALID_TYPE = "InvalidType";

    public static final String REQUIRED_STRUCT_FIELD_MISSING = "MissingRequiredStructField";
    public static final String EXTRA_STRUCT_FIELD_NOT_ALLOWED = "IllegalExtraStructField";
}

class ValidationFailure {
    public final String path;
    public final String reason;

    public ValidationFailure(String path, String reason) {
        this.path = path;
        this.reason = reason;
    }
}