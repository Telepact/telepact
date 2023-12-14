package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class _ValidateUtil {

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

    public static final String ENUM_DOES_NOT_HAVE_EXACTLY_ONE_FIELD = "EnumDoesNotHaveExactlyOneField";
    public static final String UNKNOWN_ENUM_VALUE = "UnknownEnumField";

    public static final String NUMBER_OUT_OF_RANGE = "NumberOutOfRange";

    public static final String RESULT_ENUM_DOES_NOT_HAVE_EXACTLY_ONE_FIELD = "ResultEnumDoesNotHaveExactlyOneField";
    public static final String UNKNOWN_RESULT_ENUM_VALUE = "UnknownResultEnumField";

    static List<ValidationFailure> validateHeaders(
            Map<String, Object> headers, JApiSchema jApiSchema, UFn functionType) {
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

                UStruct structReference;
                if (structName.startsWith("->.")) {
                    var resultEnumValue = structName.split("->.")[1];
                    structReference = functionType.result.values.get(resultEnumValue);
                } else if (structName.startsWith("fn.")) {
                    var functionRef = (UFn) jApiSchema.parsed.get(structName);
                    structReference = functionRef.arg;
                } else {
                    structReference = (UStruct) jApiSchema.parsed.get(structName);
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
}
