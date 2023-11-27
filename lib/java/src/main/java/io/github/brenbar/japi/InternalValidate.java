package io.github.brenbar.japi;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class InternalValidate {

    static List<ValidationFailure> validateHeaders(
            Map<String, Object> headers, JApiSchemaTuple jApiSchema, Fn functionType) {
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
                if (!structName.startsWith("struct.") && !structName.startsWith("->.")
                        && !structName.startsWith("fn.")) {
                    validationFailures.add(new ValidationFailure("headers{_sel}{%s}".formatted(structName),
                            "SelectHeaderKeyMustBeStructReference"));
                    continue;
                }

                Struct structReference;
                if (structName.startsWith("->.")) {
                    var resultEnumValue = structName.split("->.")[1];
                    structReference = functionType.result.values.get(resultEnumValue);
                } else if (structName.startsWith("fn.")) {
                    var functionRef = (Fn) jApiSchema.parsed.get(structName);
                    structReference = functionRef.arg;
                } else {
                    structReference = (Struct) jApiSchema.parsed.get(structName);
                }

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
                    if (!structReference.fields.containsKey(stringField)) {
                        validationFailures.add(new ValidationFailure(
                                "headers{_sel}{%s}[%d]".formatted(structName, i),
                                "UnknownStructField"));
                    }
                }
            }

        }

        return validationFailures;

    }

    static List<ValidationFailure> validateResultEnum(
            Enum resultEnumType,
            Map<String, Object> actualResult) {
        return validateEnumValues("", resultEnumType.values, actualResult);
    }

    static List<ValidationFailure> validateStructFields(
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

    static List<ValidationFailure> validateEnumValues(
            String path,
            Map<String, Struct> referenceValues,
            Map<?, ?> actual) {
        if (actual.size() != 1) {
            return Collections.singletonList(
                    new ValidationFailure(path,
                            ValidationErrorReasons.MULTI_ENTRY_OBJECT_INVALID_FOR_ENUM_TYPE));
        }
        var entry = actual.entrySet().stream().findFirst().get();
        var enumTarget = (String) entry.getKey();
        var enumPayload = entry.getValue();

        var nextPath = !"".equals(path) ? "%s.%s".formatted(path, enumTarget) : enumTarget;

        var referenceStruct = referenceValues.get(enumTarget);
        if (referenceStruct == null) {
            return Collections
                    .singletonList(new ValidationFailure(nextPath,
                            ValidationErrorReasons.UNKNOWN_ENUM_VALUE));
        }

        if (enumPayload instanceof Boolean) {
            return Collections.singletonList(new ValidationFailure(nextPath,
                    ValidationErrorReasons.BOOLEAN_INVALID_FOR_ENUM_STRUCT_TYPE));
        } else if (enumPayload instanceof Number) {
            return Collections.singletonList(new ValidationFailure(nextPath,
                    ValidationErrorReasons.NUMBER_INVALID_FOR_ENUM_STRUCT_TYPE));
        } else if (enumPayload instanceof String) {
            return Collections.singletonList(new ValidationFailure(nextPath,
                    ValidationErrorReasons.STRING_INVALID_FOR_ENUM_STRUCT_TYPE));
        } else if (enumPayload instanceof List) {
            return Collections.singletonList(new ValidationFailure(nextPath,
                    ValidationErrorReasons.ARRAY_INVALID_FOR_ENUM_STRUCT_TYPE));
        } else if (enumPayload instanceof Map<?, ?> m2) {
            return validateEnumStruct(nextPath, referenceStruct, enumTarget,
                    (Map<String, Object>) m2);
        } else {
            return Collections.singletonList(new ValidationFailure(nextPath,
                    ValidationErrorReasons.VALUE_INVALID_FOR_ENUM_STRUCT_TYPE));
        }
    }

    private static List<ValidationFailure> validateEnumStruct(
            String path,
            Struct enumStruct,
            String enumCase,
            Map<String, Object> actual) {
        var validationFailures = new ArrayList<ValidationFailure>();

        var nestedValidationFailures = validateStructFields(path, enumStruct.fields,
                actual);
        validationFailures.addAll(nestedValidationFailures);

        return validationFailures;
    }

    private static List<ValidationFailure> validateBoolean(String path, Object value) {
        if (value instanceof Boolean) {
            return Collections.emptyList();
        } else if (value instanceof Number) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.NUMBER_INVALID_FOR_BOOLEAN_TYPE));
        } else if (value instanceof String) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.STRING_INVALID_FOR_BOOLEAN_TYPE));
        } else if (value instanceof List) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.ARRAY_INVALID_FOR_BOOLEAN_TYPE));
        } else if (value instanceof Map) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.OBJECT_INVALID_FOR_BOOLEAN_TYPE));
        } else {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.VALUE_INVALID_FOR_BOOLEAN_TYPE));
        }
    }

    private static List<ValidationFailure> validateInteger(String path, Object value) {
        if (value instanceof Boolean) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.BOOLEAN_INVALID_FOR_INTEGER_TYPE));
        } else if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.NUMBER_OUT_OF_RANGE));
        } else if (value instanceof Number) {
            if (value instanceof Long || value instanceof Integer) {
                return Collections.emptyList();
            } else {
                return Collections.singletonList(new ValidationFailure(path,
                        ValidationErrorReasons.NUMBER_INVALID_FOR_INTEGER_TYPE));
            }
        } else if (value instanceof String) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.STRING_INVALID_FOR_INTEGER_TYPE));
        } else if (value instanceof List) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.ARRAY_INVALID_FOR_INTEGER_TYPE));
        } else if (value instanceof Map) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.OBJECT_INVALID_FOR_INTEGER_TYPE));
        } else {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.VALUE_INVALID_FOR_INTEGER_TYPE));
        }
    }

    private static List<ValidationFailure> validateNumber(String path, Object value) {
        if (value instanceof Boolean) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.BOOLEAN_INVALID_FOR_NUMBER_TYPE));
        } else if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.NUMBER_OUT_OF_RANGE));
        } else if (value instanceof Number) {
            return Collections.emptyList();
        } else if (value instanceof String) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.STRING_INVALID_FOR_NUMBER_TYPE));
        } else if (value instanceof List) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.ARRAY_INVALID_FOR_NUMBER_TYPE));
        } else if (value instanceof Map) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.OBJECT_INVALID_FOR_NUMBER_TYPE));
        } else {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.OBJECT_INVALID_FOR_NUMBER_TYPE));
        }
    }

    private static List<ValidationFailure> validateString(String path, Object value) {
        if (value instanceof Boolean) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.BOOLEAN_INVALID_FOR_STRING_TYPE));
        } else if (value instanceof Number) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.NUMBER_INVALID_FOR_STRING_TYPE));
        } else if (value instanceof String) {
            return Collections.emptyList();
        } else if (value instanceof List) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.ARRAY_INVALID_FOR_STRING_TYPE));
        } else if (value instanceof Map) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.OBJECT_INVALID_FOR_STRING_TYPE));
        } else {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.VALUE_INVALID_FOR_STRING_TYPE));
        }
    }

    private static List<ValidationFailure> validateArray(String path, Object value, JsonArray a) {
        if (value instanceof Boolean) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.BOOLEAN_INVALID_FOR_ARRAY_TYPE));
        } else if (value instanceof Number) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.NUMBER_INVALID_FOR_ARRAY_TYPE));
        } else if (value instanceof String) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.STRING_INVALID_FOR_ARRAY_TYPE));
        } else if (value instanceof List l) {
            var validationFailures = new ArrayList<ValidationFailure>();
            for (var i = 0; i < l.size(); i += 1) {
                var element = l.get(i);
                var nestedValidationFailures = validateType("%s[%s]".formatted(path, i), a.nestedType,
                        element);
                validationFailures.addAll(nestedValidationFailures);
            }
            return validationFailures;
        } else if (value instanceof Map) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.OBJECT_INVALID_FOR_ARRAY_TYPE));
        } else {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.VALUE_INVALID_FOR_ARRAY_TYPE));
        }
    }

    private static List<ValidationFailure> validateObject(String path, Object value, JsonObject o) {
        if (value instanceof Boolean) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.BOOLEAN_INVALID_FOR_OBJECT_TYPE));
        } else if (value instanceof Number) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.NUMBER_INVALID_FOR_OBJECT_TYPE));
        } else if (value instanceof String) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.STRING_INVALID_FOR_OBJECT_TYPE));
        } else if (value instanceof List) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.ARRAY_INVALID_FOR_OBJECT_TYPE));
        } else if (value instanceof Map<?, ?> m) {
            var validationFailures = new ArrayList<ValidationFailure>();
            for (Map.Entry<?, ?> entry : m.entrySet()) {
                var k = (String) entry.getKey();
                var v = entry.getValue();
                var nestedValidationFailures = validateType("%s{%s}".formatted(path, k), o.nestedType,
                        v);
                validationFailures.addAll(nestedValidationFailures);
            }
            return validationFailures;
        } else {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.VALUE_INVALID_FOR_OBJECT_TYPE));
        }
    }

    private static List<ValidationFailure> validateStruct(String path, Object value, Struct s) {
        if (value instanceof Boolean) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.BOOLEAN_INVALID_FOR_STRUCT_TYPE));
        } else if (value instanceof Number) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.NUMBER_INVALID_FOR_STRUCT_TYPE));
        } else if (value instanceof String) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.STRING_INVALID_FOR_STRUCT_TYPE));
        } else if (value instanceof List) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.ARRAY_INVALID_FOR_STRUCT_TYPE));
        } else if (value instanceof Map<?, ?> m) {
            return validateStructFields(path, s.fields, (Map<String, Object>) m);
        } else {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.VALUE_INVALID_FOR_STRUCT_TYPE));
        }
    }

    private static List<ValidationFailure> validateEnum(String path, Object value, Enum e) {
        if (value instanceof Boolean) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.BOOLEAN_INVALID_FOR_ENUM_TYPE));
        } else if (value instanceof Number) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.NUMBER_INVALID_FOR_ENUM_TYPE));
        } else if (value instanceof String) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.STRING_INVALID_FOR_ENUM_TYPE));
        } else if (value instanceof List) {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.ARRAY_INVALID_FOR_ENUM_TYPE));
        } else if (value instanceof Map<?, ?> m) {
            return validateEnumValues(path, e.values, m);
        } else {
            return Collections.singletonList(
                    new ValidationFailure(path, ValidationErrorReasons.VALUE_INVALID_FOR_ENUM_TYPE));
        }
    }

    private static List<ValidationFailure> validateType(String path, TypeDeclaration typeDeclaration,
            Object value) {
        if (value == null) {
            if (!typeDeclaration.nullable) {
                return Collections.singletonList(new ValidationFailure(path,
                        ValidationErrorReasons.NULL_INVALID_FOR_NON_NULL_TYPE));
            } else {
                return Collections.emptyList();
            }
        } else {
            var expectedType = typeDeclaration.type;
            if (expectedType instanceof JsonBoolean) {
                return validateBoolean(path, value);
            } else if (expectedType instanceof JsonInteger) {
                return validateInteger(path, value);
            } else if (expectedType instanceof JsonNumber) {
                return validateNumber(path, value);
            } else if (expectedType instanceof JsonString) {
                return validateString(path, value);
            } else if (expectedType instanceof JsonArray a) {
                return validateArray(path, value, a);
            } else if (expectedType instanceof JsonObject o) {
                return validateObject(path, value, o);
            } else if (expectedType instanceof Struct s) {
                return validateStruct(path, value, s);
            } else if (expectedType instanceof Enum e) {
                return validateEnum(path, value, e);
            } else if (expectedType instanceof Fn f) {
                return validateType(path, new TypeDeclaration(f.arg, false), value);
            } else if (expectedType instanceof Ext e) {
                return e.typeExtension.validate(path, value);
            } else if (expectedType instanceof JsonAny a) {
                // all values are valid for any
                return Collections.emptyList();
            } else {
                return Collections.singletonList(new ValidationFailure(path, ValidationErrorReasons.INVALID_TYPE));
            }
        }
    }

}
