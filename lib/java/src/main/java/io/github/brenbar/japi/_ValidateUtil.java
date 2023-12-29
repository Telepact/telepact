package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class _ValidateUtil {

    static List<ValidationFailure> validateHeaders(
            Map<String, Object> headers, JApiSchema jApiSchema, UFn functionType) {
        var validationFailures = new ArrayList<ValidationFailure>();

        if (headers.containsKey("_bin")) {
            List<Object> binaryChecksums;
            try {
                binaryChecksums = (List<Object>) headers.get("_bin");
                var i = 0;
                for (var binaryChecksum : binaryChecksums) {
                    try {
                        var integerElement = (Integer) binaryChecksum;
                    } catch (ClassCastException e) {
                        try {
                            var longElement = (Long) binaryChecksum;
                        } catch (ClassCastException e2) {
                            validationFailures
                                    .addAll(getTypeUnexpectedValidationFailure(List.of("headers", "_bin", i),
                                            binaryChecksum,
                                            "Integer"));
                        }
                    }
                    i += 1;
                }
            } catch (ClassCastException e) {
                validationFailures
                        .addAll(getTypeUnexpectedValidationFailure(List.of("headers", "_bin"), headers.get("_bin"),
                                "Array"));
            }
        }

        if (headers.containsKey("_sel")) {
            Map<String, Object> selectStructFieldsHeader = new HashMap<>();
            try {
                selectStructFieldsHeader = (Map<String, Object>) headers
                        .get("_sel");

            } catch (ClassCastException e) {
                validationFailures.addAll(getTypeUnexpectedValidationFailure(List.of("headers", "_sel"),
                        headers.get("_sel"), "Object"));
            }
            for (Map.Entry<String, Object> entry : selectStructFieldsHeader.entrySet()) {
                var structName = entry.getKey();
                if (!structName.startsWith("struct.") && !structName.startsWith("->.")
                        && !structName.startsWith("fn.")) {
                    validationFailures.add(new ValidationFailure(List.of("headers", "_sel", structName),
                            "SelectHeaderKeyMustBeStructReference", Map.of()));
                    continue;
                }

                UStruct structReference;
                if (structName.startsWith("->.")) {
                    var resultUnionValue = structName.split("->.")[1];
                    structReference = functionType.result.values.get(resultUnionValue);
                } else if (structName.startsWith("fn.")) {
                    var functionRef = (UFn) jApiSchema.parsed.get(structName);
                    structReference = functionRef.arg;
                } else {
                    structReference = (UStruct) jApiSchema.parsed.get(structName);
                }

                if (structReference == null) {
                    validationFailures.add(new ValidationFailure(List.of("headers", "_sel", structName),
                            "StructNameUnknown", Map.of()));
                    continue;
                }

                List<Object> fields = new ArrayList<>();
                try {
                    fields = (List<Object>) entry.getValue();
                } catch (ClassCastException e) {
                    validationFailures
                            .addAll(getTypeUnexpectedValidationFailure(List.of("headers", "_sel", structName),
                                    entry.getValue(),
                                    "Array"));
                }

                for (int i = 0; i < fields.size(); i += 1) {
                    var field = fields.get(i);
                    String stringField;
                    try {
                        stringField = (String) field;
                    } catch (ClassCastException e) {
                        validationFailures.addAll(getTypeUnexpectedValidationFailure(
                                List.of("headers", "_sel", structName, i),
                                field,
                                "String"));
                        continue;
                    }
                    if (!structReference.fields.containsKey(stringField)) {
                        validationFailures.add(new ValidationFailure(
                                List.of("headers", "_sel", structName, i),
                                "StructFieldUnknown", Map.of()));
                    }
                }
            }

        }

        return validationFailures;

    }

    static String getType(Object value) {
        if (value == null) {
            return "Null";
        } else if (value instanceof Boolean) {
            return "Boolean";
        } else if (value instanceof Number) {
            return "Number";
        } else if (value instanceof String) {
            return "String";
        } else if (value instanceof List) {
            return "Array";
        } else if (value instanceof Map) {
            return "Object";
        } else {
            return "Unknown";
        }
    }

    static List<ValidationFailure> getTypeUnexpectedValidationFailure(List<Object> path, Object value,
            String expectedType) {
        var actualType = _ValidateUtil.getType(value);
        Map<String, Object> data = new TreeMap<>(Map.ofEntries(Map.entry("actual", Map.of(actualType, Map.of())),
                Map.entry("expected", Map.of(expectedType, Map.of()))));
        return Collections.singletonList(
                new ValidationFailure(path, "TypeUnexpected", data));
    }

    static List<Object> prepend(Object value, List<Object> original) {
        var newList = new ArrayList<>(original);
        newList.add(0, value);
        return newList;
    }
}
