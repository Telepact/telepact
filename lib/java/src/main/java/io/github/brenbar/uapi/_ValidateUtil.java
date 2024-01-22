package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

class _ValidateUtil {

    static List<_ValidationFailure> validateHeaders(
            Map<String, Object> headers, UApiSchema uApiSchema, _UFn functionType) {
        final var validationFailures = new ArrayList<_ValidationFailure>();

        if (headers.containsKey("_bin")) {
            final List<Object> binaryChecksums;
            try {
                binaryChecksums = _CastUtil.asList(headers.get("_bin"));
                var i = 0;
                for (final var binaryChecksum : binaryChecksums) {
                    try {
                        var integerElement = _CastUtil.asInt(binaryChecksum);
                    } catch (ClassCastException e) {
                        validationFailures
                                .addAll(_Util.getTypeUnexpectedValidationFailure(List.of("_bin", i),
                                        binaryChecksum,
                                        "Integer"));
                    }
                    i += 1;
                }
            } catch (ClassCastException e) {
                validationFailures
                        .addAll(_Util.getTypeUnexpectedValidationFailure(List.of("_bin"), headers.get("_bin"),
                                "Array"));
            }
        }

        if (headers.containsKey("_sel")) {
            final var thisValidationFailures = validateSelectHeaders(headers, uApiSchema, functionType);
            validationFailures.addAll(thisValidationFailures);
        }

        return validationFailures;
    }

    private static List<_ValidationFailure> validateSelectHeaders(Map<String, Object> headers,
            UApiSchema uApiSchema, _UFn functionType) {
        Map<String, Object> selectStructFieldsHeader;
        try {
            selectStructFieldsHeader = _CastUtil.asMap(headers.get("_sel"));
        } catch (ClassCastException e) {
            return _Util.getTypeUnexpectedValidationFailure(List.of("_sel"),
                    headers.get("_sel"), "Object");
        }

        final var validationFailures = new ArrayList<_ValidationFailure>();

        for (final var entry : selectStructFieldsHeader.entrySet()) {
            final var typeName = entry.getKey();
            final var selectValue = entry.getValue();

            final _UType typeReference;
            if (typeName.equals("->")) {
                typeReference = functionType.result;
            } else {
                final Map<String, _UType> parsedTypes = uApiSchema.parsed;
                typeReference = parsedTypes.get(typeName);
            }

            if (typeReference == null) {
                validationFailures.add(new _ValidationFailure(List.of("_sel", typeName),
                        "TypeUnknown", Map.of()));
                continue;
            }

            if (typeReference instanceof final _UUnion u) {
                final Map<String, Object> unionCases;
                try {
                    unionCases = _CastUtil.asMap(selectValue);
                } catch (ClassCastException e) {
                    validationFailures.addAll(
                            _Util.getTypeUnexpectedValidationFailure(List.of("_sel", typeName), selectValue, "Object"));
                    continue;
                }

                for (final var unionCaseEntry : unionCases.entrySet()) {
                    final var unionCase = unionCaseEntry.getKey();
                    final var selectedCaseStructFields = unionCaseEntry.getValue();
                    final var structRef = u.cases.get(unionCase);

                    final List<Object> loopPath = List.of("_sel", typeName, unionCase);

                    if (structRef == null) {
                        validationFailures.add(new _ValidationFailure(
                                loopPath,
                                "UnionCaseUnknown", Map.of()));
                        continue;
                    }

                    final var nestedValidationFailures = validateSelectStruct(structRef, loopPath,
                            selectedCaseStructFields);

                    validationFailures.addAll(nestedValidationFailures);
                }
            } else if (typeReference instanceof final _UFn f) {
                final _UUnion fnCall = f.call;
                final Map<String, _UStruct> fnCallCases = fnCall.cases;
                final String fnName = f.name;
                final var argStruct = fnCallCases.get(fnName);
                final var nestedValidationFailures = validateSelectStruct(argStruct, List.of("_sel", typeName),
                        selectValue);

                validationFailures.addAll(nestedValidationFailures);
            } else {
                final var structRef = (_UStruct) typeReference;
                final var nestedValidationFailures = validateSelectStruct(structRef, List.of("_sel", typeName),
                        selectValue);

                validationFailures.addAll(nestedValidationFailures);
            }
        }

        return validationFailures;
    }

    private static List<_ValidationFailure> validateSelectStruct(_UStruct structReference, List<Object> basePath,
            Object selectedFields) {
        final var validationFailures = new ArrayList<_ValidationFailure>();

        final List<Object> fields;
        try {
            fields = _CastUtil.asList(selectedFields);
        } catch (ClassCastException e) {
            return _Util.getTypeUnexpectedValidationFailure(basePath, selectedFields, "Array");
        }

        for (int i = 0; i < fields.size(); i += 1) {
            var field = fields.get(i);
            String stringField;
            try {
                stringField = _CastUtil.asString(field);
            } catch (ClassCastException e) {
                final List<Object> thisPath = _ValidateUtil.append(basePath, i);

                validationFailures.addAll(_Util.getTypeUnexpectedValidationFailure(thisPath, field, "String"));
                continue;
            }
            if (!structReference.fields.containsKey(stringField)) {
                final List<Object> thisPath = _ValidateUtil.append(basePath, i);

                validationFailures.add(new _ValidationFailure(thisPath, "StructFieldUnknown", Map.of()));
            }
        }

        return validationFailures;
    }

    static List<Object> prepend(Object value, List<Object> original) {
        final var newList = new ArrayList<>(original);

        newList.add(0, value);
        return newList;
    }

    static List<Object> append(List<Object> original, Object value) {
        final var newList = new ArrayList<>(original);

        newList.add(value);
        return newList;
    }
}
