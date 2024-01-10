package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

class _ValidateUtil {

    static List<ValidationFailure> validateHeaders(
            Map<String, Object> headers, JApiSchema jApiSchema, UFn functionType) {
        var validationFailures = new ArrayList<ValidationFailure>();

        if (headers.containsKey("_bin")) {
            List<Object> binaryChecksums;
            try {
                binaryChecksums = _CastUtil.asList(headers.get("_bin"));
                var i = 0;
                for (var binaryChecksum : binaryChecksums) {
                    try {
                        var integerElement = _CastUtil.asInt(binaryChecksum);
                    } catch (ClassCastException e) {
                        try {
                            var longElement = _CastUtil.asLong(binaryChecksum);
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
                selectStructFieldsHeader = _CastUtil.asMap(headers.get("_sel"));

            } catch (ClassCastException e) {
                validationFailures.addAll(getTypeUnexpectedValidationFailure(List.of("headers", "_sel"),
                        headers.get("_sel"), "Object"));
            }
            for (Map.Entry<String, Object> entry : selectStructFieldsHeader.entrySet()) {
                var structName = entry.getKey();

                UStruct structReference;
                if (structName.startsWith("->.")) {
                    var resultUnionCase = structName.split("->.")[1];
                    structReference = functionType.result.values.get(resultUnionCase);
                } else if (structName.startsWith("fn.")) {
                    var functionRef = (UFn) jApiSchema.parsed.get(structName);
                    structReference = functionRef.call.values.get(functionRef.name);
                } else if (structName.startsWith("struct.")) {
                    structReference = (UStruct) jApiSchema.parsed.get(structName);
                } else {
                    structReference = null;
                }

                if (structReference == null) {
                    validationFailures.add(new ValidationFailure(List.of("headers", "_sel", structName),
                            "StructUnknown", Map.of()));
                    continue;
                }

                List<Object> fields = new ArrayList<>();
                try {
                    fields = _CastUtil.asList(entry.getValue());
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
                        stringField = _CastUtil.asString(field);
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

    static List<Object> append(List<Object> original, Object value) {
        var newList = new ArrayList<>(original);
        newList.add(value);
        return newList;
    }
}
