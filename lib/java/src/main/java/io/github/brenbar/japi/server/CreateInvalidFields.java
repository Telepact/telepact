package io.github.brenbar.japi.server;

import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

class CreateInvalidFields {

    static Map.Entry<String, Map<String, List<Map<String, String>>>> createInvalidField(Error.InvalidFieldType e) {
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
}
