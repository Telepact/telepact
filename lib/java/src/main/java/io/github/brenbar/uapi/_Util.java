package io.github.brenbar.uapi;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

class _Util {

    static final String _ANY_NAME = "Any";
    static final String _ARRAY_NAME = "Array";
    static final String _BOOLEAN_NAME = "Boolean";
    static final String _FN_NAME = "Object";
    static final String _INTEGER_NAME = "Integer";
    static final String _MOCK_CALL_NAME = "_ext._Call";
    static final String _MOCK_STUB_NAME = "_ext._Stub";
    static final String _NUMBER_NAME = "Number";
    static final String _OBJECT_NAME = "Object";
    static final String _STRING_NAME = "String";
    static final String _STRUCT_NAME = "Object";
    static final String _UNION_NAME = "Object";

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

    static List<_ValidationFailure> getTypeUnexpectedValidationFailure(List<Object> path, Object value,
            String expectedType) {
        final var actualType = getType(value);
        final Map<String, Object> data = new TreeMap<>(Map.ofEntries(Map.entry("actual", Map.of(actualType, Map.of())),
                Map.entry("expected", Map.of(expectedType, Map.of()))));
        return List.of(
                new _ValidationFailure(path, "TypeUnexpected", data));
    }

    static Object generateRandomAny(_RandomGenerator randomGenerator) {
        final var selectType = randomGenerator.nextInt(3);
        if (selectType == 0) {
            return randomGenerator.nextBoolean();
        } else if (selectType == 1) {
            return randomGenerator.nextInt();
        } else {
            return randomGenerator.nextString();
        }
    }

    static List<_ValidationFailure> validateArray(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        if (value instanceof final List l) {
            final var nestedTypeDeclaration = typeParameters.get(0);

            final var validationFailures = new ArrayList<_ValidationFailure>();
            for (var i = 0; i < l.size(); i += 1) {
                final var element = l.get(i);
                final var nestedValidationFailures = nestedTypeDeclaration.validate(element, generics);
                final var index = i;

                final var nestedValidationFailuresWithPath = new ArrayList<_ValidationFailure>();
                for (var f : nestedValidationFailures) {
                    final List<Object> finalPath = _ValidateUtil.prepend(index, f.path);
                    nestedValidationFailuresWithPath.add(new _ValidationFailure(finalPath, f.reason,
                            f.data));
                }

                validationFailures.addAll(nestedValidationFailuresWithPath);
            }

            return validationFailures;
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value,
                    _ARRAY_NAME);
        }
    }

    static Object generateRandomArray(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        final var nestedTypeDeclaration = typeParameters.get(0);

        if (useStartingValue) {
            final var startingArray = (List<Object>) startingValue;

            final var array = new ArrayList<Object>();
            for (final var startingArrayValue : startingArray) {
                final var value = nestedTypeDeclaration.generateRandomValue(startingArrayValue, true,
                        includeRandomOptionalFields, generics, randomGenerator);

                array.add(value);
            }

            return array;
        } else {
            final var length = randomGenerator.nextCollectionLength();

            final var array = new ArrayList<Object>();
            for (int i = 0; i < length; i += 1) {
                final var value = nestedTypeDeclaration.generateRandomValue(null, false,
                        includeRandomOptionalFields,
                        generics, randomGenerator);

                array.add(value);
            }

            return array;
        }
    }

    static List<_ValidationFailure> validateBoolean(Object value) {
        if (value instanceof Boolean) {
            return List.of();
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _BOOLEAN_NAME);
        }
    }

    static Object generateRandomBoolean(Object startingValue, boolean useStartingValue,
            _RandomGenerator randomGenerator) {
        if (useStartingValue) {
            return startingValue;
        } else {
            return randomGenerator.nextBoolean();
        }
    }

    static Object generateRandomFn(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator, Map<String, _UStruct> callCases) {
        if (useStartingValue) {
            final var startingFnValue = (Map<String, Object>) startingValue;
            return constructRandomUnion(callCases, startingFnValue, includeRandomOptionalFields,
                    List.of(), randomGenerator);
        } else {
            return constructRandomUnion(callCases, new HashMap<>(), includeRandomOptionalFields,
                    List.of(), randomGenerator);
        }
    }

    static List<_ValidationFailure> validateInteger(Object value) {
        if (value instanceof Long || value instanceof Integer) {
            return List.of();
        } else if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
            return List.of(
                    new _ValidationFailure(new ArrayList<Object>(), "NumberOutOfRange", Map.of()));
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _INTEGER_NAME);
        }
    }

    static Object generateRandomInteger(Object startingValue, boolean useStartingValue,
            _RandomGenerator randomGenerator) {
        if (useStartingValue) {
            return startingValue;
        } else {
            return randomGenerator.nextInt();
        }
    }

    static List<_ValidationFailure> validateMockCall(Object givenObj,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, Map<String, _UType> types) {
        final Map<String, Object> givenMap;
        try {
            givenMap = _CastUtil.asMap(givenObj);
        } catch (ClassCastException e) {
            return getTypeUnexpectedValidationFailure(new ArrayList<Object>(), givenObj, "Object");
        }

        final var regexString = "^fn\\..*$";

        final var matches = givenMap.keySet().stream().filter(k -> k.matches(regexString)).toList();
        if (matches.size() != 1) {
            return List.of(new _ValidationFailure(new ArrayList<Object>(), "ObjectKeyRegexMatchCountUnexpected",
                    Map.of("regex", regexString, "actual", matches.size(), "expected", 1)));
        }

        final var functionName = matches.get(0);
        final var functionDef = (_UFn) types.get(functionName);
        final var input = givenMap.get(functionName);

        final _UUnion functionDefCall = functionDef.call;
        final String functionDefName = functionDef.name;
        final Map<String, _UStruct> functionDefCallCases = functionDefCall.cases;

        final var inputFailures = functionDefCallCases.get(functionDefName).validate(input, List.of(), List.of());

        final var inputFailuresWithPath = new ArrayList<_ValidationFailure>();
        for (var f : inputFailures) {
            List<Object> newPath = _ValidateUtil.prepend(functionName, f.path);

            inputFailuresWithPath.add(new _ValidationFailure(newPath, f.reason, f.data));
        }

        return inputFailuresWithPath.stream()
                .filter(f -> !f.reason.equals("RequiredStructFieldMissing")).toList();
    }

    static List<_ValidationFailure> validateMockStub(Object givenObj,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, Map<String, _UType> types) {
        final var validationFailures = new ArrayList<_ValidationFailure>();

        final Map<String, Object> givenMap;
        try {
            givenMap = _CastUtil.asMap(givenObj);
        } catch (ClassCastException e) {
            return getTypeUnexpectedValidationFailure(List.of(), givenObj, "Object");
        }

        final var regexString = "^fn\\..*$";

        final var matches = givenMap.keySet().stream().filter(k -> k.matches(regexString)).toList();
        if (matches.size() != 1) {
            return List.of(
                    new _ValidationFailure(List.of(),
                            "ObjectKeyRegexMatchCountUnexpected",
                            Map.of("regex", regexString, "actual",
                                    matches.size(), "expected", 1)));

        }

        final var functionName = matches.get(0);
        final var functionDef = (_UFn) types.get(functionName);
        final var input = givenMap.get(functionName);

        final _UUnion functionDefCall = functionDef.call;
        final String functionDefName = functionDef.name;
        final Map<String, _UStruct> functionDefCallCases = functionDefCall.cases;
        final var inputFailures = functionDefCallCases.get(functionDefName).validate(input, List.of(), List.of());

        final var inputFailuresWithPath = new ArrayList<_ValidationFailure>();
        for (final var f : inputFailures) {
            final List<Object> thisPath = _ValidateUtil.prepend(functionName, f.path);

            inputFailuresWithPath.add(new _ValidationFailure(thisPath, f.reason, f.data));
        }

        final var inputFailuresWithoutMissingRequired = inputFailuresWithPath.stream()
                .filter(f -> !Objects.equals(f.reason, "RequiredStructFieldMissing")).toList();

        validationFailures.addAll(inputFailuresWithoutMissingRequired);

        final var resultDefKey = "->";

        if (!givenMap.containsKey(resultDefKey)) {
            return List.of(new _ValidationFailure(List.of(resultDefKey),
                    "RequiredObjectKeyMissing",
                    Map.of()));
        }

        final var output = givenMap.get(resultDefKey);
        final var outputFailures = functionDef.result.validate(output, List.of(), List.of());

        final var outputFailuresWithPath = new ArrayList<_ValidationFailure>();
        for (final var f : outputFailures) {
            final List<Object> thisPath = _ValidateUtil.prepend(resultDefKey, f.path);

            outputFailuresWithPath.add(new _ValidationFailure(thisPath, f.reason, f.data));
        }

        final var failuresWithoutMissingRequired = outputFailuresWithPath
                .stream()
                .filter(f -> !Objects.equals(f.reason, "RequiredStructFieldMissing"))
                .toList();

        validationFailures.addAll(failuresWithoutMissingRequired);

        return validationFailures;
    }

    static List<_ValidationFailure> validateNumber(Object value) {
        if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
            return List.of(
                    new _ValidationFailure(List.of(), "NumberOutOfRange", Map.of()));
        } else if (value instanceof Number) {
            return List.of();
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _NUMBER_NAME);
        }
    }

    static Object generateRandomNumber(Object startingValue, boolean useStartingValue,
            _RandomGenerator randomGenerator) {
        if (useStartingValue) {
            return startingValue;
        } else {
            return randomGenerator.nextDouble();
        }
    }

    static List<_ValidationFailure> validateObject(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        if (value instanceof final Map<?, ?> m) {
            final var nestedTypeDeclaration = typeParameters.get(0);

            final var validationFailures = new ArrayList<_ValidationFailure>();
            for (Map.Entry<?, ?> entry : m.entrySet()) {
                final var k = (String) entry.getKey();
                final var v = entry.getValue();
                final var nestedValidationFailures = nestedTypeDeclaration.validate(v, generics);

                final var nestedValidationFailuresWithPath = new ArrayList<_ValidationFailure>();
                for (var f : nestedValidationFailures) {
                    final List<Object> thisPath = _ValidateUtil.prepend(k, f.path);

                    nestedValidationFailuresWithPath.add(new _ValidationFailure(thisPath, f.reason, f.data));
                }

                validationFailures.addAll(nestedValidationFailuresWithPath);
            }

            return validationFailures;
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _OBJECT_NAME);
        }
    }

    static Object generateRandomObject(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator) {
        final var nestedTypeDeclaration = typeParameters.get(0);

        if (useStartingValue) {
            final var startingObj = (Map<String, Object>) startingValue;

            final var obj = new TreeMap<String, Object>();
            for (final var startingObjEntry : startingObj.entrySet()) {
                final var key = startingObjEntry.getKey();
                final var startingObjValue = startingObjEntry.getValue();
                final var value = nestedTypeDeclaration.generateRandomValue(startingObjValue, true,
                        includeRandomOptionalFields, generics, randomGenerator);
                obj.put(key, value);
            }

            return obj;
        } else {
            final var length = randomGenerator.nextCollectionLength();

            final var obj = new TreeMap<String, Object>();
            for (int i = 0; i < length; i += 1) {
                final var key = randomGenerator.nextString();
                final var value = nestedTypeDeclaration.generateRandomValue(null, false, includeRandomOptionalFields,
                        generics, randomGenerator);
                obj.put(key, value);
            }

            return obj;
        }
    }

    static List<_ValidationFailure> validateString(Object value) {
        if (value instanceof String) {
            return List.of();
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _STRING_NAME);
        }
    }

    static Object generateRandomString(Object startingValue, boolean useStartingValue,
            _RandomGenerator randomGenerator) {
        if (useStartingValue) {
            return startingValue;
        } else {
            return randomGenerator.nextString();
        }
    }

    static List<_ValidationFailure> validateStruct(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, Map<String, _UFieldDeclaration> fields) {
        if (value instanceof Map<?, ?> m) {
            return validateStructFields(fields, (Map<String, Object>) m, typeParameters);
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _STRUCT_NAME);
        }
    }

    static List<_ValidationFailure> validateStructFields(
            Map<String, _UFieldDeclaration> fields,
            Map<String, Object> actualStruct, List<_UTypeDeclaration> typeParameters) {
        final var validationFailures = new ArrayList<_ValidationFailure>();

        final var missingFields = new ArrayList<String>();
        for (final var entry : fields.entrySet()) {
            final var fieldName = entry.getKey();
            final var fieldDeclaration = entry.getValue();
            final boolean isOptional = fieldDeclaration.optional;
            if (!actualStruct.containsKey(fieldName) && !isOptional) {
                missingFields.add(fieldName);
            }
        }

        for (final var missingField : missingFields) {
            final var validationFailure = new _ValidationFailure(List.of(missingField),
                    "RequiredStructFieldMissing",
                    Map.of());

            validationFailures.add(validationFailure);
        }

        for (final var entry : actualStruct.entrySet()) {
            final var fieldName = entry.getKey();
            final var fieldValue = entry.getValue();

            final var referenceField = fields.get(fieldName);
            if (referenceField == null) {
                var validationFailure = new _ValidationFailure(List.of(fieldName), "StructFieldUnknown",
                        Map.of());

                validationFailures.add(validationFailure);
                continue;
            }

            final _UTypeDeclaration refFieldTypeDeclaration = referenceField.typeDeclaration;

            final var nestedValidationFailures = refFieldTypeDeclaration.validate(fieldValue, typeParameters);

            final var nestedValidationFailuresWithPath = new ArrayList<_ValidationFailure>();
            for (final var f : nestedValidationFailures) {
                final List<Object> thisPath = _ValidateUtil.prepend(fieldName, f.path);

                nestedValidationFailuresWithPath.add(new _ValidationFailure(thisPath, f.reason, f.data));
            }

            validationFailures.addAll(nestedValidationFailuresWithPath);
        }

        return validationFailures;
    }

    static Object generateRandomStruct(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator random, Map<String, _UFieldDeclaration> fields) {
        if (useStartingValue) {
            final var startingStructValue = (Map<String, Object>) startingValue;
            return constructRandomStruct(fields, startingStructValue, includeRandomOptionalFields,
                    typeParameters, random);
        } else {
            return constructRandomStruct(fields, new HashMap<>(), includeRandomOptionalFields,
                    typeParameters, random);
        }
    }

    static Map<String, Object> constructRandomStruct(
            Map<String, _UFieldDeclaration> referenceStruct, Map<String, Object> startingStruct,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            _RandomGenerator randomGenerator) {

        final var sortedReferenceStruct = new ArrayList<>(referenceStruct.entrySet());
        Collections.sort(sortedReferenceStruct, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

        final var obj = new TreeMap<String, Object>();
        for (final var field : sortedReferenceStruct) {
            final var fieldName = field.getKey();
            final var fieldDeclaration = field.getValue();
            final var startingValue = startingStruct.get(fieldName);
            final var useStartingValue = startingStruct.containsKey(fieldName);

            final Object value;
            if (useStartingValue) {
                value = fieldDeclaration.typeDeclaration.generateRandomValue(startingValue, useStartingValue,
                        includeRandomOptionalFields, typeParameters, randomGenerator);
            } else {
                if (!fieldDeclaration.optional) {
                    value = fieldDeclaration.typeDeclaration.generateRandomValue(null, false,
                            includeRandomOptionalFields, typeParameters, randomGenerator);
                } else {
                    if (!includeRandomOptionalFields) {
                        continue;
                    }
                    if (randomGenerator.nextBoolean()) {
                        continue;
                    }
                    value = fieldDeclaration.typeDeclaration.generateRandomValue(null, false,
                            includeRandomOptionalFields, typeParameters, randomGenerator);
                }
            }

            obj.put(fieldName, value);
        }
        return obj;
    }

    static List<_ValidationFailure> validateValueOfType(Object value, List<_UTypeDeclaration> generics,
            _UType thisType, boolean nullable, List<_UTypeDeclaration> typeParameters) {
        if (value == null) {
            final boolean isNullable;
            if (thisType instanceof _UGeneric g) {
                final int genericIndex = g.index;
                final var generic = generics.get(genericIndex);
                isNullable = generic.nullable;
            } else {
                isNullable = nullable;
            }

            if (!isNullable) {
                return getTypeUnexpectedValidationFailure(List.of(), value,
                        thisType.getName(generics));
            } else {
                return List.of();
            }
        } else {
            return thisType.validate(value, typeParameters, generics);
        }
    }

    static Object generateRandomValueOfType(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator, _UType thisType, boolean nullable,
            List<_UTypeDeclaration> typeParameters) {
        if (nullable && !useStartingValue && randomGenerator.nextBoolean()) {
            return null;
        } else {
            return thisType.generateRandomValue(startingValue, useStartingValue, includeRandomOptionalFields,
                    typeParameters, generics, randomGenerator);
        }
    }

    static List<_ValidationFailure> validateUnion(Object value, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, Map<String, _UStruct> cases) {
        if (value instanceof Map<?, ?> m) {
            return validateUnionCases(cases, m, typeParameters);
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _UNION_NAME);
        }
    }

    private static List<_ValidationFailure> validateUnionCases(
            Map<String, _UStruct> referenceCases,
            Map<?, ?> actual, List<_UTypeDeclaration> typeParameters) {
        if (actual.size() != 1) {
            return List.of(
                    new _ValidationFailure(new ArrayList<Object>(),
                            "ZeroOrManyUnionFieldsDisallowed", Map.of()));
        }

        final var entry = _Util.unionEntry((Map<String, Object>) actual);
        final var unionTarget = (String) entry.getKey();
        final var unionPayload = entry.getValue();

        final var referenceStruct = referenceCases.get(unionTarget);
        if (referenceStruct == null) {
            return Collections
                    .singletonList(new _ValidationFailure(List.of(unionTarget),
                            "UnionFieldUnknown", Map.of()));
        }

        if (unionPayload instanceof Map<?, ?> m2) {
            final var nestedValidationFailures = validateUnionStruct(referenceStruct, unionTarget,
                    (Map<String, Object>) m2, typeParameters);

            final var nestedValidationFailuresWithPath = new ArrayList<_ValidationFailure>();
            for (final var f : nestedValidationFailures) {
                final List<Object> thisPath = _ValidateUtil.prepend(unionTarget, f.path);

                nestedValidationFailuresWithPath.add(new _ValidationFailure(thisPath, f.reason, f.data));
            }

            return nestedValidationFailuresWithPath;
        } else {
            return getTypeUnexpectedValidationFailure(List.of(unionTarget),
                    unionPayload, "Object");
        }
    }

    private static List<_ValidationFailure> validateUnionStruct(
            _UStruct unionStruct,
            String unionCase,
            Map<String, Object> actual, List<_UTypeDeclaration> typeParameters) {
        return validateStructFields(unionStruct.fields, actual, typeParameters);
    }

    static Object generateRandomUnion(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator random, Map<String, _UStruct> cases) {
        if (useStartingValue) {
            final var startingUnionCase = (Map<String, Object>) startingValue;
            return constructRandomUnion(cases, startingUnionCase, includeRandomOptionalFields,
                    typeParameters, random);
        } else {
            return constructRandomUnion(cases, new HashMap<>(), includeRandomOptionalFields,
                    typeParameters, random);
        }
    }

    static Map<String, Object> constructRandomUnion(Map<String, _UStruct> unionCasesReference,
            Map<String, Object> startingUnion,
            boolean includeRandomOptionalFields,
            List<_UTypeDeclaration> typeParameters,
            _RandomGenerator randomGenerator) {
        if (!startingUnion.isEmpty()) {
            final var unionEntry = _Util.unionEntry(startingUnion);
            final var unionCase = unionEntry.getKey();
            final var unionStructType = unionCasesReference.get(unionCase);
            final var unionStartingStruct = (Map<String, Object>) startingUnion.get(unionCase);

            return Map.of(unionCase, constructRandomStruct(unionStructType.fields, unionStartingStruct,
                    includeRandomOptionalFields, typeParameters, randomGenerator));
        } else {
            final var sortedUnionCasesReference = new ArrayList<>(unionCasesReference.entrySet());

            Collections.sort(sortedUnionCasesReference, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

            final var randomIndex = randomGenerator.nextInt(sortedUnionCasesReference.size());
            final var unionEntry = sortedUnionCasesReference.get(randomIndex);
            final var unionCase = unionEntry.getKey();
            final var unionData = unionEntry.getValue();

            return Map.of(unionCase,
                    constructRandomStruct(unionData.fields, new HashMap<>(), includeRandomOptionalFields,
                            typeParameters, randomGenerator));
        }
    }

    static Map.Entry<String, Object> unionEntry(Map<String, Object> union) {
        return union.entrySet().stream().findAny().orElse(null);
    }
}
