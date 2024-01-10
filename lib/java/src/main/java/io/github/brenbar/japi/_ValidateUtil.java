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
                        validationFailures
                                .addAll(getTypeUnexpectedValidationFailure(List.of("_bin", i),
                                        binaryChecksum,
                                        "Integer"));
                    }
                    i += 1;
                }
            } catch (ClassCastException e) {
                validationFailures
                        .addAll(getTypeUnexpectedValidationFailure(List.of("_bin"), headers.get("_bin"),
                                "Array"));
            }
        }

        if (headers.containsKey("_sel")) {
            Map<String, Object> selectStructFieldsHeader = new HashMap<>();
            try {
                selectStructFieldsHeader = _CastUtil.asMap(headers.get("_sel"));

            } catch (ClassCastException e) {
                validationFailures.addAll(getTypeUnexpectedValidationFailure(List.of("_sel"),
                        headers.get("_sel"), "Object"));
            }
            for (var entry : selectStructFieldsHeader.entrySet()) {
                var typeName = entry.getKey();
                var selectValue = entry.getValue();

                UType typeReference;
                if (typeName.equals("->")) {
                    typeReference = functionType.result;
                } else {
                    typeReference = jApiSchema.parsed.get(typeName);
                }

                if (typeReference == null) {
                    validationFailures.add(new ValidationFailure(List.of("_sel", typeName),
                            "StructUnknown", Map.of()));
                    continue;
                }

                if (typeReference instanceof UUnion u) {
                    Map<String, Object> unionCases;
                    try {
                        unionCases = _CastUtil.asMap(selectValue);
                    } catch (ClassCastException e) {
                        validationFailures.addAll(
                                getTypeUnexpectedValidationFailure(List.of("_sel", "->"), selectValue, "Object"));
                        continue;
                    }

                    for (var unionCaseEntry : unionCases.entrySet()) {
                        var unionCase = unionCaseEntry.getKey();
                        var selectedCaseStructFields = unionCaseEntry.getValue();

                        var structRef = u.cases.get(unionCase);

                        List<Object> loopPath = List.of("_sel", typeName, unionCase);

                        if (structRef == null) {
                            validationFailures.add(new ValidationFailure(
                                    loopPath,
                                    "UnionCaseUnknown", Map.of()));
                            continue;
                        }

                        var nestedValidationFailures = validateSelectStruct(structRef, loopPath,
                                selectedCaseStructFields);
                        validationFailures.addAll(nestedValidationFailures);
                    }
                } else if (typeReference instanceof UFn f) {
                    var argStruct = f.call.cases.get(f.name);
                    var nestedValidationFailures = validateSelectStruct(argStruct, List.of("_sel", typeName),
                            selectValue);
                    validationFailures.addAll(nestedValidationFailures);
                } else {
                    var structRef = (UStruct) typeReference;
                    var nestedValidationFailures = validateSelectStruct(structRef, List.of("_sel", typeName),
                            selectValue);
                    validationFailures.addAll(nestedValidationFailures);
                }

            }

        }

        return validationFailures;
    }

    private static List<ValidationFailure> validateSelectStruct(UStruct structReference, List<Object> basePath,
            Object selectedFields) {
        var validationFailures = new ArrayList<ValidationFailure>();

        List<Object> fields = new ArrayList<>();
        try {
            fields = _CastUtil.asList(selectedFields);
        } catch (ClassCastException e) {
            validationFailures
                    .addAll(getTypeUnexpectedValidationFailure(basePath,
                            selectedFields,
                            "Array"));
        }

        for (int i = 0; i < fields.size(); i += 1) {
            var field = fields.get(i);
            String stringField;
            try {
                stringField = _CastUtil.asString(field);
            } catch (ClassCastException e) {
                validationFailures.addAll(getTypeUnexpectedValidationFailure(
                        _ValidateUtil.append(basePath, i),
                        field,
                        "String"));
                continue;
            }
            if (!structReference.fields.containsKey(stringField)) {
                validationFailures.add(new ValidationFailure(
                        _ValidateUtil.append(basePath, i),
                        "StructFieldUnknown", Map.of()));
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
