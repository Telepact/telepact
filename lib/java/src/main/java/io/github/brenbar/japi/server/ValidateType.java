package io.github.brenbar.japi.server;

import io.github.brenbar.japi.Parser;

import java.util.List;
import java.util.Map;

class ValidateType {

    static void validateType(String fieldName, Parser.TypeDeclaration typeDeclaration, Object value) {
        if (value == null) {
            if (!typeDeclaration.nullable()) {
                throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.NULL_INVALID_FOR_NON_NULL_TYPE);
            } else {
                return;
            }
        } else {
            var expectedType = typeDeclaration.type();
            if (expectedType instanceof Parser.JsonBoolean) {
                if (value instanceof Boolean) {
                    return;
                } else if (value instanceof Number) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_BOOLEAN_TYPE);
                } else if (value instanceof String) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_BOOLEAN_TYPE);
                } else if (value instanceof List) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_BOOLEAN_TYPE);
                } else if (value instanceof Map) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_BOOLEAN_TYPE);
                } else {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_BOOLEAN_TYPE);
                }
            } else if (expectedType instanceof Parser.JsonInteger) {
                if (value instanceof Boolean) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_INTEGER_TYPE);
                } else if (value instanceof Number) {
                    if (value instanceof Long || value instanceof Integer) {
                        return;
                    } else {
                        throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_INTEGER_TYPE);
                    }
                } else if (value instanceof String) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_INTEGER_TYPE);
                } else if (value instanceof List) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_INTEGER_TYPE);
                } else if (value instanceof Map) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_INTEGER_TYPE);
                } else {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_INTEGER_TYPE);
                }
            } else if (expectedType instanceof Parser.JsonNumber) {
                if (value instanceof Boolean) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_NUMBER_TYPE);
                } else if (value instanceof Number) {
                    return;
                } else if (value instanceof String) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_NUMBER_TYPE);
                } else if (value instanceof List) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_NUMBER_TYPE);
                } else if (value instanceof Map) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_NUMBER_TYPE);
                } else {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_NUMBER_TYPE);
                }
            } else if (expectedType instanceof Parser.JsonString) {
                if (value instanceof Boolean) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_STRING_TYPE);
                } else if (value instanceof Number) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_STRING_TYPE);
                } else if (value instanceof String) {
                    return;
                } else if (value instanceof List) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_STRING_TYPE);
                } else if (value instanceof Map) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_STRING_TYPE);
                } else {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_STRING_TYPE);
                }
            } else if (expectedType instanceof Parser.JsonArray a) {
                if (value instanceof Boolean) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ARRAY_TYPE);
                } else if (value instanceof Number) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_ARRAY_TYPE);
                } else if (value instanceof String) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_ARRAY_TYPE);
                } else if (value instanceof List l) {
                    for (var i = 0; i < l.size(); i += 1) {
                        var element = l.get(i);
                        validateType("%s[%s]".formatted(fieldName, i), a.nestedType(), element);
                    }
                    return;
                } else if (value instanceof Map) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.OBJECT_INVALID_FOR_ARRAY_TYPE);
                } else {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_ARRAY_TYPE);
                }
            } else if (expectedType instanceof Parser.JsonObject o) {
                if (value instanceof Boolean) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_OBJECT_TYPE);
                } else if (value instanceof Number) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_OBJECT_TYPE);
                } else if (value instanceof String) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_OBJECT_TYPE);
                } else if (value instanceof List) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_OBJECT_TYPE);
                } else if (value instanceof Map<?, ?> m) {
                    for (Map.Entry<?, ?> entry : m.entrySet()) {
                        var k = (String) entry.getKey();
                        var v = entry.getValue();
                        validateType("%s{%s}".formatted(fieldName, k), o.nestedType(), v);
                    }
                    return;
                } else {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_OBJECT_TYPE);
                }
            } else if (expectedType instanceof Parser.Struct s) {
                if (value instanceof Boolean) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_STRUCT_TYPE);
                } else if (value instanceof Number) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_STRUCT_TYPE);
                } else if (value instanceof String) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_STRUCT_TYPE);
                } else if (value instanceof List) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_STRUCT_TYPE);
                } else if (value instanceof Map<?, ?> m) {
                    ValidateStruct.validate(fieldName, s.fields(), (Map<String, Object>) m);
                    return;
                } else {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_STRUCT_TYPE);
                }
            } else if (expectedType instanceof Parser.Enum u) {
                if (value instanceof Boolean) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ENUM_TYPE);
                } else if (value instanceof Number) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_ENUM_TYPE);
                } else if (value instanceof String) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_ENUM_TYPE);
                } else if (value instanceof List) {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_ENUM_TYPE);
                } else if (value instanceof Map<?, ?> m) {
                    if (m.size() != 1) {
                        throw new Error.EnumDoesNotHaveOnlyOneField(fieldName);
                    }
                    var entry = m.entrySet().stream().findFirst().get();
                    var enumCase = (String) entry.getKey();
                    var enumValue = entry.getValue();

                    if (enumValue instanceof Boolean) {
                        throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.BOOLEAN_INVALID_FOR_ENUM_STRUCT_TYPE);
                    } else if (enumValue instanceof Number) {
                        throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.NUMBER_INVALID_FOR_ENUM_STRUCT_TYPE);
                    } else if (enumValue instanceof String) {
                        throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.STRING_INVALID_FOR_ENUM_STRUCT_TYPE);
                    } else if (enumValue instanceof List) {
                        throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.ARRAY_INVALID_FOR_ENUM_STRUCT_TYPE);
                    } else if (enumValue instanceof Map<?, ?> m2) {
                        ValidateEnum.validateEnum(fieldName, u.cases(), enumCase, (Map<String, Object>) m2);
                        return;
                    } else {
                        throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_ENUM_STRUCT_TYPE);
                    }
                } else {
                    throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.VALUE_INVALID_FOR_ENUM_TYPE);
                }
            } else if (expectedType instanceof Parser.JsonAny a) {
                // all values validate for any
            } else {
                throw new Error.InvalidFieldType(fieldName, InvalidFieldTypeError.INVALID_TYPE);
            }
        }
    }
}
