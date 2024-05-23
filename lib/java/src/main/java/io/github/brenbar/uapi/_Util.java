package io.github.brenbar.uapi;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.function.BiFunction;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.zip.CRC32;

import org.msgpack.jackson.dataformat.MessagePackExtensionType;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

class _Util {

    static final String _ANY_NAME = "Any";
    static final String _ARRAY_NAME = "Array";
    static final String _BOOLEAN_NAME = "Boolean";
    static final String _FN_NAME = "Object";
    static final String _INTEGER_NAME = "Integer";
    static final String _MOCK_CALL_NAME = "_ext.Call_";
    static final String _MOCK_STUB_NAME = "_ext.Stub_";
    static final String _NUMBER_NAME = "Number";
    static final String _OBJECT_NAME = "Object";
    static final String _STRING_NAME = "String";
    static final String _STRUCT_NAME = "Object";
    static final String _UNION_NAME = "Object";
    static final String _SELECT = "Object";

    public static String getInternalUApiJson() {
        final var stream = Thread.currentThread().getContextClassLoader().getResourceAsStream("internal.uapi.json");
        return new BufferedReader(new InputStreamReader(stream)).lines().collect(Collectors.joining("\n"));
    };

    public static String getMockUApiJson() {
        final var stream = Thread.currentThread().getContextClassLoader()
                .getResourceAsStream("mock-internal.uapi.json");
        return new BufferedReader(new InputStreamReader(stream)).lines().collect(Collectors.joining("\n"));
    };

    public static Integer asInt(Object object) {
        if (object == null) {
            throw new ClassCastException();
        }

        return (Integer) object;
    }

    public static String asString(Object object) {
        if (object == null) {
            throw new ClassCastException();
        }

        return (String) object;
    }

    public static List<Object> asList(Object object) {
        if (object == null) {
            throw new ClassCastException();
        }

        return (List<Object>) object;
    }

    public static Map<String, Object> asMap(Object object) {
        if (object == null) {
            throw new ClassCastException();
        }

        return (Map<String, Object>) object;
    }

    public static List<_SchemaParseFailure> offsetSchemaIndex(List<_SchemaParseFailure> initialFailures, int offset,
            Map<String, Integer> schemaKeysToIndex, Set<Integer> errorIndices) {
        final var finalList = new ArrayList<_SchemaParseFailure>();

        final var indexToSchemaKey = schemaKeysToIndex.entrySet().stream()
                .collect(Collectors.toMap(e -> e.getValue(), e -> e.getKey()));

        for (final var f : initialFailures) {
            final String reason = f.reason;
            final List<Object> path = f.path;
            final Map<String, Object> data = f.data;
            final var newPath = new ArrayList<>(path);

            final var originalIndex = (Integer) newPath.get(0);
            newPath.set(0, originalIndex - offset);

            final Map<String, Object> finalData;
            if (reason.equals("PathCollision")) {
                final var otherNewPath = new ArrayList<>((List<Object>) data.get("other"));

                otherNewPath.set(0, (Integer) otherNewPath.get(0) - offset);
                finalData = Map.of("other", otherNewPath);
            } else {
                finalData = data;
            }

            String schemaKey;
            if (errorIndices.contains(originalIndex)) {
                schemaKey = "errors";
            } else {
                schemaKey = indexToSchemaKey.get(originalIndex);
            }

            finalList.add(new _SchemaParseFailure(newPath, reason, finalData, schemaKey));
        }

        return finalList;
    }

    public static String findSchemaKey(Map<String, Object> definition, int index) {
        final var regex = "^(errors|((fn|requestHeader|responseHeader|info)|((struct|union|_ext)(<[0-2]>)?))\\..*)";
        final var matches = new ArrayList<String>();

        final var keys = definition.keySet().stream().sorted().toList();

        for (final var e : keys) {
            if (e.matches(regex)) {
                matches.add(e);
            }
        }

        if (matches.size() == 1) {
            return matches.get(0);
        } else {
            throw new UApiSchemaParseError(List.of(new _SchemaParseFailure(List.of(index),
                    "ObjectKeyRegexMatchCountUnexpected",
                    new TreeMap<>(
                            Map.of("regex", regex, "actual", matches.size(), "expected", 1, "keys", keys)),
                    null)));
        }
    }

    public static String findMatchingSchemaKey(Set<String> schemaKeys, String schemaKey) {
        for (final var k : schemaKeys) {
            if (Objects.equals(k, schemaKey)) {
                return k;
            }
        }
        return null;
    }

    public static List<_SchemaParseFailure> getTypeUnexpectedParseFailure(List<Object> path, Object value,
            String expectedType) {
        final var actualType = getType(value);
        final Map<String, Object> data = new TreeMap<>(Map.ofEntries(Map.entry("actual", Map.of(actualType, Map.of())),
                Map.entry("expected", Map.of(expectedType, Map.of()))));
        return List.of(
                new _SchemaParseFailure(path, "TypeUnexpected", data, null));
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

    static _UTypeDeclaration parseTypeDeclaration(List<Object> path, List<Object> typeDeclarationArray,
            int thisTypeParameterCount, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<_SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        if (typeDeclarationArray.isEmpty()) {
            throw new UApiSchemaParseError(List.of(new _SchemaParseFailure(path,
                    "EmptyArrayDisallowed", Map.of(), null)));
        }

        final List<Object> basePath = append(path, 0);
        final var baseType = typeDeclarationArray.get(0);

        final String rootTypeString;
        try {
            rootTypeString = asString(baseType);
        } catch (ClassCastException e) {
            final List<_SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(basePath,
                    baseType, "String");
            throw new UApiSchemaParseError(thisParseFailures);
        }

        final var regexString = "^(.+?)(\\?)?$";
        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(rootTypeString);
        if (!matcher.find()) {
            throw new UApiSchemaParseError(List.of(new _SchemaParseFailure(basePath,
                    "StringRegexMatchFailed", Map.of("regex", regexString), null)));
        }

        final var typeName = matcher.group(1);
        final var nullable = matcher.group(2) != null;

        final _UType type = getOrParseType(basePath, typeName, thisTypeParameterCount, uApiSchemaPseudoJson,
                schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures, failedTypes);

        if (type instanceof _UGeneric && nullable) {
            throw new UApiSchemaParseError(List.of(new _SchemaParseFailure(basePath,
                    "StringRegexMatchFailed", Map.of("regex", "^(.+?)[^\\?]$"), null)));
        }

        final var givenTypeParameterCount = typeDeclarationArray.size() - 1;
        if (type.getTypeParameterCount() != givenTypeParameterCount) {
            throw new UApiSchemaParseError(List.of(new _SchemaParseFailure(path,
                    "ArrayLengthUnexpected",
                    Map.of("actual", typeDeclarationArray.size(), "expected", type.getTypeParameterCount() + 1),
                    null)));
        }

        final var parseFailures = new ArrayList<_SchemaParseFailure>();
        final var typeParameters = new ArrayList<_UTypeDeclaration>();
        final var givenTypeParameters = typeDeclarationArray.subList(1, typeDeclarationArray.size());

        var index = 0;
        for (final var e : givenTypeParameters) {
            index += 1;
            final List<Object> loopPath = append(path, index);

            final List<Object> l;
            try {
                l = asList(e);
            } catch (ClassCastException e1) {
                final List<_SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(loopPath, e,
                        "Array");

                parseFailures.addAll(thisParseFailures);
                continue;
            }

            final _UTypeDeclaration typeParameterTypeDeclaration;
            try {
                typeParameterTypeDeclaration = parseTypeDeclaration(loopPath, l, thisTypeParameterCount,
                        uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                        failedTypes);

                typeParameters.add(typeParameterTypeDeclaration);
            } catch (UApiSchemaParseError e2) {
                parseFailures.addAll(e2.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        return new _UTypeDeclaration(type, nullable, typeParameters);
    }

    static _UType getOrParseType(List<Object> path, String typeName, int thisTypeParameterCount,
            List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions, List<_SchemaParseFailure> allParseFailures,
            Set<String> failedTypes) {
        if (failedTypes.contains(typeName)) {
            throw new UApiSchemaParseError(List.of());
        }

        final var existingType = parsedTypes.get(typeName);
        if (existingType != null) {
            return existingType;
        }

        final String genericRegex;
        if (thisTypeParameterCount > 0) {
            genericRegex = "|(T.([%s]))"
                    .formatted(thisTypeParameterCount > 1 ? "0-%d".formatted(thisTypeParameterCount - 1) : "0");
        } else {
            genericRegex = "";
        }

        final var regexString = "^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*)%s)$"
                .formatted(genericRegex);
        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(typeName);
        if (!matcher.find()) {
            throw new UApiSchemaParseError(List.of(new _SchemaParseFailure(path,
                    "StringRegexMatchFailed", Map.of("regex", regexString), null)));
        }

        final var standardTypeName = matcher.group(1);
        if (standardTypeName != null) {
            return switch (standardTypeName) {
                case "boolean" -> new _UBoolean();
                case "integer" -> new _UInteger();
                case "number" -> new _UNumber();
                case "string" -> new _UString();
                case "array" -> new _UArray();
                case "object" -> new _UObject();
                default -> new _UAny();
            };
        }

        if (thisTypeParameterCount > 0) {
            final var genericParameterIndexString = matcher.group(9);
            if (genericParameterIndexString != null) {
                final var genericParameterIndex = Integer.parseInt(genericParameterIndexString);
                return new _UGeneric(genericParameterIndex);
            }
        }

        final var customTypeName = matcher.group(2);
        final var index = schemaKeysToIndex.get(customTypeName);
        if (index == null) {
            throw new UApiSchemaParseError(List.of(new _SchemaParseFailure(path,
                    "TypeUnknown", Map.of("name", customTypeName), null)));
        }
        final var definition = (Map<String, Object>) uApiSchemaPseudoJson.get(index);

        final var typeParameterCountString = matcher.group(6);
        final int typeParameterCount;
        if (typeParameterCountString != null) {
            typeParameterCount = Integer.parseInt(typeParameterCountString);
        } else {
            typeParameterCount = 0;
        }

        try {
            final _UType type;
            if (customTypeName.startsWith("struct")) {
                type = parseStructType(List.of(index), definition, customTypeName, List.of(),
                        typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions,
                        allParseFailures, failedTypes);
            } else if (customTypeName.startsWith("union")) {
                type = parseUnionType(List.of(index), definition, customTypeName, List.of(), List.of(),
                        typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes,
                        typeExtensions, allParseFailures, failedTypes);
            } else if (customTypeName.startsWith("fn")) {
                type = parseFunctionType(List.of(index), definition, customTypeName,
                        uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                        failedTypes);
            } else {
                type = typeExtensions.get(customTypeName);
                if (type == null) {
                    throw new UApiSchemaParseError(List.of(new _SchemaParseFailure(List.of(index),
                            "TypeExtensionImplementationMissing", Map.of("name", customTypeName), null)));
                }
            }

            parsedTypes.put(customTypeName, type);

            return type;
        } catch (UApiSchemaParseError e) {
            allParseFailures.addAll(e.schemaParseFailures);
            failedTypes.add(customTypeName);
            throw new UApiSchemaParseError(List.of());
        }
    }

    static _UStruct parseStructType(List<Object> path, Map<String, Object> structDefinitionAsPseudoJson,
            String schemaKey, List<String> ignoreKeys, int typeParameterCount, List<Object> uApiSchemaPseudoJson,
            Map<String, Integer> schemaKeysToIndex, Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions,
            List<_SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var parseFailures = new ArrayList<_SchemaParseFailure>();
        final var otherKeys = new HashSet<>(structDefinitionAsPseudoJson.keySet());

        otherKeys.remove(schemaKey);
        otherKeys.remove("///");
        otherKeys.remove("_ignoreIfDuplicate");
        for (final var ignoreKey : ignoreKeys) {
            otherKeys.remove(ignoreKey);
        }

        if (otherKeys.size() > 0) {
            for (final var k : otherKeys) {
                final List<Object> loopPath = append(path, k);

                parseFailures.add(new _SchemaParseFailure(loopPath, "ObjectKeyDisallowed", Map.of(), null));
            }
        }

        final List<Object> thisPath = append(path, schemaKey);
        final Object defInit = structDefinitionAsPseudoJson.get(schemaKey);

        Map<String, Object> definition = null;
        try {
            definition = asMap(defInit);
        } catch (ClassCastException e) {
            final List<_SchemaParseFailure> branchParseFailures = getTypeUnexpectedParseFailure(thisPath,
                    defInit, "Object");

            parseFailures.addAll(branchParseFailures);
        }

        if (parseFailures.size() > 0) {
            throw new UApiSchemaParseError(parseFailures);
        }

        final var fields = parseStructFields(definition, thisPath, typeParameterCount,
                uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                failedTypes);

        return new _UStruct(schemaKey, fields, typeParameterCount);
    }

    static _UUnion parseUnionType(List<Object> path, Map<String, Object> unionDefinitionAsPseudoJson, String schemaKey,
            List<String> ignoreKeys, List<String> requiredKeys, int typeParameterCount,
            List<Object> uApiSchemaPseudoJson,
            Map<String, Integer> schemaKeysToIndex, Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions,
            List<_SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var parseFailures = new ArrayList<_SchemaParseFailure>();

        final var otherKeys = new HashSet<>(unionDefinitionAsPseudoJson.keySet());

        otherKeys.remove(schemaKey);
        otherKeys.remove("///");
        for (final var ignoreKey : ignoreKeys) {
            otherKeys.remove(ignoreKey);
        }

        if (otherKeys.size() > 0) {
            for (final var k : otherKeys) {
                final List<Object> loopPath = append(path, k);

                parseFailures.add(new _SchemaParseFailure(loopPath, "ObjectKeyDisallowed", Map.of(), null));
            }
        }

        final List<Object> thisPath = append(path, schemaKey);
        final Object defInit = unionDefinitionAsPseudoJson.get(schemaKey);

        final List<Object> definition2;
        try {
            definition2 = asList(defInit);
        } catch (ClassCastException e) {
            final List<_SchemaParseFailure> finalParseFailures = getTypeUnexpectedParseFailure(thisPath,
                    defInit, "Array");

            parseFailures.addAll(finalParseFailures);
            throw new UApiSchemaParseError(parseFailures);
        }

        final List<Map<String, Object>> definition = new ArrayList<>();
        int index = -1;
        for (final var element : definition2) {
            index += 1;
            final List<Object> loopPath = append(thisPath, index);
            try {
                definition.add(asMap(element));
            } catch (ClassCastException e) {
                final List<_SchemaParseFailure> finalParseFailures = getTypeUnexpectedParseFailure(loopPath,
                        element, "Object");

                parseFailures.addAll(finalParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        if (definition.isEmpty() && requiredKeys.isEmpty()) {
            parseFailures.add(new _SchemaParseFailure(thisPath, "EmptyArrayDisallowed", Map.of(), null));
        } else {
            outerLoop: for (final var requiredKey : requiredKeys) {
                for (final var element : definition) {
                    final var map = asMap(element);
                    final var keys = new HashSet<>(map.keySet());
                    keys.remove("///");
                    if (keys.contains(requiredKey)) {
                        continue outerLoop;
                    }
                }
                final List<Object> branchPath = append(append(thisPath, 0), requiredKey);
                parseFailures.add(new _SchemaParseFailure(branchPath, "RequiredObjectKeyMissing", Map.of(), null));
            }
        }

        final var cases = new HashMap<String, _UStruct>();
        final var caseIndices = new HashMap<String, Integer>();

        for (int i = 0; i < definition.size(); i++) {
            final var element = definition.get(i);
            final List<Object> loopPath = append(thisPath, i);

            final var mapInit = asMap(element);
            final var map = new HashMap<>(mapInit);
            map.remove("///");
            final var keys = new ArrayList<>(map.keySet());

            final var regexString = "^([A-Z][a-zA-Z0-9_]*)$";

            final var matches = keys.stream().filter(k -> k.matches(regexString)).toList();
            if (matches.size() != 1) {
                parseFailures.add(
                        new _SchemaParseFailure(loopPath,
                                "ObjectKeyRegexMatchCountUnexpected",
                                Map.of("regex", regexString, "actual",
                                        matches.size(), "expected", 1, "keys", keys),
                                null));
                continue;
            }
            if (map.size() != 1) {
                parseFailures.add(new _SchemaParseFailure(loopPath, "ObjectSizeUnexpected",
                        Map.of("expected", 1, "actual", map.size()), null));
                continue;
            }

            final var entry = unionEntry(map);
            final var unionCase = entry.getKey();
            final List<Object> unionKeyPath = append(loopPath, unionCase);

            final Map<String, Object> unionCaseStruct;
            try {
                unionCaseStruct = asMap(entry.getValue());
            } catch (ClassCastException e) {
                List<_SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(unionKeyPath,
                        entry.getValue(), "Object");

                parseFailures.addAll(thisParseFailures);
                continue;
            }

            final Map<String, _UFieldDeclaration> fields;
            try {
                fields = parseStructFields(unionCaseStruct, unionKeyPath, typeParameterCount,
                        uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                        failedTypes);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
                continue;
            }

            final var unionStruct = new _UStruct("%s.%s".formatted(schemaKey, unionCase), fields, typeParameterCount);

            cases.put(unionCase, unionStruct);
            caseIndices.put(unionCase, i);
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        return new _UUnion(schemaKey, cases, caseIndices, typeParameterCount);
    }

    static Map<String, _UFieldDeclaration> parseStructFields(Map<String, Object> referenceStruct, List<Object> path,
            int typeParameterCount, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<_SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var parseFailures = new ArrayList<_SchemaParseFailure>();
        final var fields = new HashMap<String, _UFieldDeclaration>();

        for (final var structEntry : referenceStruct.entrySet()) {
            final var fieldDeclaration = structEntry.getKey();

            for (final var existingField : fields.keySet()) {
                final var existingFieldNoOpt = existingField.split("!")[0];
                final var fieldNoOpt = fieldDeclaration.split("!")[0];
                if (fieldNoOpt.equals(existingFieldNoOpt)) {
                    final List<Object> finalPath = append(path, fieldDeclaration);
                    final List<Object> finalOtherPath = append(path, existingField);

                    parseFailures
                            .add(new _SchemaParseFailure(finalPath, "PathCollision",
                                    Map.of("other", finalOtherPath), null));
                }
            }

            final var typeDeclarationValue = structEntry.getValue();

            final _UFieldDeclaration parsedField;
            try {
                parsedField = parseField(path, fieldDeclaration,
                        typeDeclarationValue, typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex,
                        parsedTypes,
                        typeExtensions, allParseFailures, failedTypes);
                final String fieldName = parsedField.fieldName;

                fields.put(fieldName, parsedField);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        return fields;
    }

    static _UFieldDeclaration parseField(List<Object> path, String fieldDeclaration, Object typeDeclarationValue,
            int typeParameterCount, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<_SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var regexString = "^([a-z][a-zA-Z0-9_]*)(!)?$";
        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(fieldDeclaration);
        if (!matcher.find()) {
            final List<Object> finalPath = append(path, fieldDeclaration);
            throw new UApiSchemaParseError(List.of(new _SchemaParseFailure(finalPath,
                    "KeyRegexMatchFailed", Map.of("regex", regexString), null)));
        }

        final var fieldName = matcher.group(0);
        final var optional = matcher.group(2) != null;
        final List<Object> thisPath = append(path, fieldName);

        final List<Object> typeDeclarationArray;
        try {
            typeDeclarationArray = asList(typeDeclarationValue);
        } catch (ClassCastException e) {
            throw new UApiSchemaParseError(
                    getTypeUnexpectedParseFailure(thisPath, typeDeclarationValue, "Array"));
        }

        final var typeDeclaration = parseTypeDeclaration(thisPath,
                typeDeclarationArray, typeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions, allParseFailures, failedTypes);

        return new _UFieldDeclaration(fieldName, typeDeclaration, optional);
    }

    static void applyErrorToParsedTypes(int errorIndex, _UError error, Map<String, _UType> parsedTypes,
            Map<String, Integer> schemaKeysToIndex) {
        var parseFailures = new ArrayList<_SchemaParseFailure>();
        for (var parsedType : parsedTypes.entrySet()) {
            _UFn f;
            try {
                f = (_UFn) parsedType.getValue();
            } catch (ClassCastException e) {
                continue;
            }

            String fnName = f.name;

            var regex = Pattern.compile(f.errorsRegex);

            _UUnion fnResult = f.result;
            Map<String, _UStruct> fnResultCases = fnResult.cases;
            _UUnion errorErrors = error.errors;
            Map<String, _UStruct> errorCases = errorErrors.cases;

            for (var errorCase : errorCases.entrySet()) {
                var newKey = errorCase.getKey();

                var matcher = regex.matcher(newKey);
                if (!matcher.find()) {
                    continue;
                }

                if (fnResultCases.containsKey(newKey)) {
                    final var otherPathIndex = schemaKeysToIndex.get(fnName);
                    final var errorCaseIndex = error.errors.caseIndices.get(newKey);
                    final var fnErrorCaseIndex = f.result.caseIndices.get(newKey);
                    parseFailures.add(new _SchemaParseFailure(List.of(errorIndex, "errors", errorCaseIndex, newKey),
                            "PathCollision", Map.of("other", List.of(otherPathIndex, "->", fnErrorCaseIndex, newKey)),
                            null));
                }
                fnResultCases.put(newKey, errorCase.getValue());
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }
    }

    public static _UError parseErrorType(Map<String, Object> errorDefinitionAsParsedJson,
            List<Object> uApiSchemaPseudoJson, int index, Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions, List<_SchemaParseFailure> allParseFailures,
            Set<String> failedTypes) {
        final var schemaKey = "errors";
        final List<Object> basePath = List.of(index);

        final var parseFailures = new ArrayList<_SchemaParseFailure>();

        final var otherKeys = new HashSet<>(errorDefinitionAsParsedJson.keySet());

        otherKeys.remove(schemaKey);
        otherKeys.remove("///");

        if (otherKeys.size() > 0) {
            for (final var k : otherKeys) {
                final List<Object> loopPath = append(basePath, k);

                parseFailures.add(new _SchemaParseFailure(loopPath, "ObjectKeyDisallowed", Map.of(), null));
            }
        }

        if (parseFailures.size() > 0) {
            throw new UApiSchemaParseError(parseFailures);
        }

        final var typeParameterCount = 0;

        final _UUnion error = parseUnionType(basePath, errorDefinitionAsParsedJson, schemaKey, List.of(), List.of(),
                typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions,
                allParseFailures, failedTypes);

        return new _UError(schemaKey, error);
    }

    static _UFieldDeclaration parseHeadersType(Map<String, Object> headersDefinitionAsParsedJson, String schemaKey,
            String headerField,
            int index, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<_SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final List<Object> path = List.of(index, schemaKey);

        var typeDeclarationValue = headersDefinitionAsParsedJson.get(schemaKey);

        final List<Object> typeDeclarationArray;
        try {
            typeDeclarationArray = asList(typeDeclarationValue);
        } catch (ClassCastException e) {
            throw new UApiSchemaParseError(
                    getTypeUnexpectedParseFailure(path, typeDeclarationValue, "Array"));
        }

        final var typeParameterCount = 0;

        try {
            final var typeDeclaration = parseTypeDeclaration(path,
                    typeDeclarationArray, typeParameterCount,
                    uApiSchemaPseudoJson,
                    schemaKeysToIndex,
                    parsedTypes,
                    typeExtensions, allParseFailures, failedTypes);

            return new _UFieldDeclaration(headerField, typeDeclaration, false);
        } catch (UApiSchemaParseError e) {
            throw new UApiSchemaParseError(e.schemaParseFailures);
        }
    }

    static _UFn parseFunctionType(List<Object> path, Map<String, Object> functionDefinitionAsParsedJson,
            String schemaKey, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<_SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var parseFailures = new ArrayList<_SchemaParseFailure>();
        final var typeParameterCount = 0;

        _UUnion callType = null;
        try {
            final _UStruct argType = parseStructType(path, functionDefinitionAsParsedJson,
                    schemaKey, List.of("->", "_errors"), typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex,
                    parsedTypes,
                    typeExtensions,
                    allParseFailures, failedTypes);
            callType = new _UUnion(schemaKey, Map.of(schemaKey, argType), Map.of(schemaKey, 0), typeParameterCount);
        } catch (UApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        final var resultSchemaKey = "->";
        final List<Object> resPath = append(path, resultSchemaKey);

        _UUnion resultType = null;
        if (!functionDefinitionAsParsedJson.containsKey(resultSchemaKey)) {
            parseFailures.add(new _SchemaParseFailure(resPath, "RequiredObjectKeyMissing", Map.of(), null));
        } else {
            try {
                resultType = parseUnionType(path, functionDefinitionAsParsedJson,
                        resultSchemaKey, functionDefinitionAsParsedJson.keySet().stream().toList(), List.of("Ok_"),
                        typeParameterCount, uApiSchemaPseudoJson,
                        schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures, failedTypes);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        final var errorsRegexKey = "_errors";
        final var regexPath = append(path, errorsRegexKey);

        String errorsRegex = null;
        if (functionDefinitionAsParsedJson.containsKey(errorsRegexKey) && !schemaKey.endsWith("_")) {
            parseFailures.add(new _SchemaParseFailure(regexPath, "ObjectKeyDisallowed", Map.of(), null));
        } else {
            final Object errorsRegexInit = functionDefinitionAsParsedJson.getOrDefault(errorsRegexKey,
                    "^.*$");
            try {
                errorsRegex = asString(errorsRegexInit);
            } catch (ClassCastException e) {
                final List<_SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(
                        regexPath, errorsRegexInit, "String");

                parseFailures
                        .addAll(thisParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        return new _UFn(schemaKey, callType, resultType, errorsRegex);
    }

    static void catchErrorCollisions(List<Object> uApiSchemaPseudoJson, Set<Integer> errorIndices,
            Map<String, Integer> keysToIndex) {
        final var parseFailures = new ArrayList<_SchemaParseFailure>();

        final var indices = errorIndices.stream().sorted().toList();

        for (var i = 0; i < indices.size(); i += 1) {
            for (var j = i + 1; j < indices.size(); j += 1) {
                final var index = indices.get(i);
                final var otherIndex = indices.get(j);

                final var def = (Map<String, Object>) uApiSchemaPseudoJson.get(index);
                final var otherDef = (Map<String, Object>) uApiSchemaPseudoJson.get(otherIndex);

                final var errDef = (List<Object>) def.get("errors");
                final var otherErrDef = (List<Object>) otherDef.get("errors");

                for (int k = 0; k < errDef.size(); k += 1) {
                    final var thisErrDef = asMap(errDef.get(k));
                    final var thisErrDefKeys = new HashSet<>(thisErrDef.keySet());
                    thisErrDefKeys.remove("///");

                    for (int l = 0; l < otherErrDef.size(); l += 1) {
                        final var thisOtherErrDef = asMap(otherErrDef.get(l));
                        final var thisOtherErrDefKeys = new HashSet<>(thisOtherErrDef.keySet());
                        thisOtherErrDefKeys.remove("///");

                        if (thisErrDefKeys.equals(thisOtherErrDefKeys)) {
                            final var thisErrorDefKey = thisErrDefKeys.stream().findFirst().get();
                            final var thisOtherErrorDefKey = thisOtherErrDefKeys.stream().findFirst().get();
                            parseFailures.add(new _SchemaParseFailure(
                                    List.of(otherIndex, "errors", l, thisOtherErrorDefKey), "PathCollision",
                                    Map.of("other", List.of(index, "errors", k, thisErrorDefKey)), "errors"));
                        }
                    }
                }
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }
    }

    static UApiSchema newUApiSchema(String uApiSchemaJson, Map<String, _UType> typeExtensions) {
        final var objectMapper = new ObjectMapper();

        final Object uApiSchemaPseudoJsonInit;
        try {
            uApiSchemaPseudoJsonInit = objectMapper.readValue(uApiSchemaJson, new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new UApiSchemaParseError(
                    List.of(new _SchemaParseFailure(List.of(), "JsonInvalid", Map.of(), null)),
                    e);
        }

        final List<Object> uApiSchemaPseudoJson;
        try {
            uApiSchemaPseudoJson = asList(uApiSchemaPseudoJsonInit);
        } catch (ClassCastException e) {
            final List<_SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(List.of(),
                    uApiSchemaPseudoJsonInit, "Array");
            throw new UApiSchemaParseError(thisParseFailures, e);
        }

        return parseUApiSchema(uApiSchemaPseudoJson, typeExtensions, 0);
    }

    static UApiSchema extendUApiSchema(UApiSchema first, String secondUApiSchemaJson,
            Map<String, _UType> secondTypeExtensions) {
        final var objectMapper = new ObjectMapper();

        final Object secondUApiSchemaPseudoJsonInit;
        try {
            secondUApiSchemaPseudoJsonInit = objectMapper.readValue(secondUApiSchemaJson, new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new UApiSchemaParseError(
                    List.of(new _SchemaParseFailure(List.of(), "JsonInvalid", Map.of(), null)),
                    e);
        }

        final List<Object> secondUApiSchemaPseudoJson;
        try {
            secondUApiSchemaPseudoJson = asList(secondUApiSchemaPseudoJsonInit);
        } catch (ClassCastException e) {
            final List<_SchemaParseFailure> thisParseFailure = getTypeUnexpectedParseFailure(List.of(),
                    secondUApiSchemaPseudoJsonInit, "Array");
            throw new UApiSchemaParseError(thisParseFailure, e);
        }

        final List<Object> firstOriginal = first.original;
        final Map<String, _UType> firstTypeExtensions = first.typeExtensions;

        final var original = new ArrayList<Object>();

        original.addAll(firstOriginal);
        original.addAll(secondUApiSchemaPseudoJson);

        final var typeExtensions = new HashMap<String, _UType>();

        typeExtensions.putAll(firstTypeExtensions);
        typeExtensions.putAll(secondTypeExtensions);

        return parseUApiSchema(original, typeExtensions, firstOriginal.size());
    }

    private static UApiSchema parseUApiSchema(List<Object> uApiSchemaPseudoJson,
            Map<String, _UType> typeExtensions, int pathOffset) {
        final var parsedTypes = new HashMap<String, _UType>();
        final var parseFailures = new ArrayList<_SchemaParseFailure>();
        final var failedTypes = new HashSet<String>();
        final var schemaKeysToIndex = new HashMap<String, Integer>();
        final var schemaKeys = new HashSet<String>();

        final var errorIndices = new HashSet<Integer>();

        var index = -1;
        for (final var definition : uApiSchemaPseudoJson) {
            index += 1;

            final List<Object> loopPath = List.of(index);

            final Map<String, Object> def;
            try {
                def = asMap(definition);
            } catch (ClassCastException e) {
                final List<_SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(loopPath,
                        definition, "Object");

                parseFailures.addAll(thisParseFailures);
                continue;
            }

            final String schemaKey;
            try {
                schemaKey = findSchemaKey(def, index);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
                continue;
            }

            if (schemaKey.equals("errors")) {
                errorIndices.add(index);
                continue;
            }

            final var ignoreIfDuplicate = (Boolean) def.getOrDefault("_ignoreIfDuplicate", false);
            final var matchingSchemaKey = findMatchingSchemaKey(schemaKeys, schemaKey);
            if (matchingSchemaKey != null) {
                if (!ignoreIfDuplicate) {
                    final var otherPathIndex = schemaKeysToIndex.get(matchingSchemaKey);
                    final List<Object> finalPath = append(loopPath, schemaKey);

                    parseFailures.add(new _SchemaParseFailure(finalPath, "PathCollision",
                            Map.of("other", List.of(otherPathIndex, matchingSchemaKey)), schemaKey));
                }
                continue;
            }

            schemaKeys.add(schemaKey);
            schemaKeysToIndex.put(schemaKey, index);
        }

        if (!parseFailures.isEmpty()) {
            final var offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset, schemaKeysToIndex,
                    errorIndices);
            throw new UApiSchemaParseError(offsetParseFailures);
        }

        final var requestHeaderKeys = new HashSet<String>();
        final var responseHeaderKeys = new HashSet<String>();
        final var rootTypeParameterCount = 0;

        for (final var schemaKey : schemaKeys) {
            if (schemaKey.startsWith("info.")) {
                continue;
            } else if (schemaKey.startsWith("requestHeader.")) {
                requestHeaderKeys.add(schemaKey);
                continue;
            } else if (schemaKey.startsWith("responseHeader.")) {
                responseHeaderKeys.add(schemaKey);
                continue;
            }

            final var thisIndex = schemaKeysToIndex.get(schemaKey);

            try {
                getOrParseType(List.of(thisIndex), schemaKey, rootTypeParameterCount,
                        uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions, parseFailures,
                        failedTypes);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            final var offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset, schemaKeysToIndex,
                    errorIndices);
            throw new UApiSchemaParseError(offsetParseFailures);
        }

        try {
            catchErrorCollisions(uApiSchemaPseudoJson, errorIndices, schemaKeysToIndex);

            for (final var thisIndex : errorIndices) {
                final var def = (Map<String, Object>) uApiSchemaPseudoJson.get(thisIndex);

                try {
                    final var error = parseErrorType(def, uApiSchemaPseudoJson, thisIndex,
                            schemaKeysToIndex, parsedTypes, typeExtensions, parseFailures, failedTypes);
                    applyErrorToParsedTypes(thisIndex, error, parsedTypes, schemaKeysToIndex);
                } catch (UApiSchemaParseError e) {
                    parseFailures.addAll(e.schemaParseFailures);
                }
            }

        } catch (UApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        final Map<String, _UFieldDeclaration> requestHeaders = new HashMap<>();
        final Map<String, _UFieldDeclaration> responseHeaders = new HashMap<>();

        try {
            for (final var requestHeaderKey : requestHeaderKeys) {
                final var thisIndex = schemaKeysToIndex.get(requestHeaderKey);
                final var def = (Map<String, Object>) uApiSchemaPseudoJson.get(thisIndex);
                final var headerField = requestHeaderKey.substring("requestHeader.".length());

                try {
                    final var requestHeaderType = parseHeadersType(def, requestHeaderKey, headerField, thisIndex,
                            uApiSchemaPseudoJson,
                            schemaKeysToIndex, parsedTypes, typeExtensions, parseFailures, failedTypes);
                    requestHeaders.put(requestHeaderType.fieldName, requestHeaderType);
                } catch (UApiSchemaParseError e) {
                    parseFailures.addAll(e.schemaParseFailures);
                }
            }
            for (final var responseHeaderKey : responseHeaderKeys) {
                final var thisIndex = schemaKeysToIndex.get(responseHeaderKey);
                final var def = (Map<String, Object>) uApiSchemaPseudoJson.get(thisIndex);
                final var headerField = responseHeaderKey.substring("responseHeader.".length());

                try {
                    final var responseHeaderType = parseHeadersType(def, responseHeaderKey, headerField, thisIndex,
                            uApiSchemaPseudoJson,
                            schemaKeysToIndex, parsedTypes, typeExtensions, parseFailures, failedTypes);
                    responseHeaders.put(responseHeaderType.fieldName, responseHeaderType);
                } catch (UApiSchemaParseError e) {
                    parseFailures.addAll(e.schemaParseFailures);
                }
            }

        } catch (UApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        if (!parseFailures.isEmpty()) {
            final var offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset, schemaKeysToIndex,
                    errorIndices);
            throw new UApiSchemaParseError(offsetParseFailures);
        }

        return new UApiSchema(uApiSchemaPseudoJson, parsedTypes, requestHeaders, responseHeaders, typeExtensions);
    }

    public static final byte PACKED_BYTE = (byte) 17;
    public static final byte UNDEFINED_BYTE = (byte) 18;

    private static class _BinaryPackNode {
        public final Integer value;
        public final Map<Integer, _BinaryPackNode> nested;

        public _BinaryPackNode(Integer value, Map<Integer, _BinaryPackNode> nested) {
            this.value = value;
            this.nested = nested;
        }
    }

    static Map<Object, Object> packBody(Map<Object, Object> body) {
        final var result = new HashMap<Object, Object>();

        for (final var entry : body.entrySet()) {
            final var packedValue = pack(entry.getValue());
            result.put(entry.getKey(), packedValue);
        }

        return result;
    }

    static Object pack(Object value) {
        if (value instanceof final List l) {
            return packList(l);
        } else if (value instanceof final Map<?, ?> m) {
            final var newMap = new HashMap<Object, Object>();

            for (final var entry : m.entrySet()) {
                newMap.put(entry.getKey(), pack(entry.getValue()));
            }

            return newMap;
        } else {
            return value;
        }
    }

    static class CannotPack extends Exception {
    }

    static List<Object> packList(List<Object> list) {
        if (list.isEmpty()) {
            return list;
        }

        final var packedList = new ArrayList<Object>();
        final var header = new ArrayList<Object>();

        packedList.add(new MessagePackExtensionType(PACKED_BYTE, new byte[0]));

        header.add(null);

        packedList.add(header);

        final var keyIndexMap = new HashMap<Integer, _BinaryPackNode>();
        try {
            for (final var e : list) {
                if (e instanceof final Map<?, ?> m) {
                    final var row = packMap(m, header, keyIndexMap);

                    packedList.add(row);
                } else {
                    // This list cannot be packed, abort
                    throw new CannotPack();
                }
            }
            return packedList;
        } catch (final CannotPack ex) {
            final var newList = new ArrayList<Object>();
            for (final var e : list) {
                newList.add(pack(e));
            }
            return newList;
        }
    }

    static List<Object> packMap(Map<?, ?> m, List<Object> header,
            Map<Integer, _BinaryPackNode> keyIndexMap) throws CannotPack {
        final var row = new ArrayList<Object>();
        for (final var entry : m.entrySet()) {
            if (entry.getKey() instanceof final String s) {
                throw new CannotPack();
            }

            final var key = (Integer) entry.getKey();
            final var keyIndex = keyIndexMap.get(key);

            final _BinaryPackNode finalKeyIndex;
            if (keyIndex == null) {
                finalKeyIndex = new _BinaryPackNode(header.size() - 1, new HashMap<>());

                if (entry.getValue() instanceof Map<?, ?>) {
                    header.add(new ArrayList<>(List.of(key)));
                } else {
                    header.add(key);
                }

                keyIndexMap.put(key, finalKeyIndex);
            } else {
                finalKeyIndex = keyIndex;
            }

            final Integer keyIndexValue = finalKeyIndex.value;
            final Map<Integer, _BinaryPackNode> keyIndexNested = finalKeyIndex.nested;

            final Object packedValue;
            if (entry.getValue() instanceof Map<?, ?> m2) {
                final List<Object> nestedHeader;
                try {
                    nestedHeader = (List<Object>) header.get(keyIndexValue + 1);
                } catch (ClassCastException e) {
                    // No nesting available, so the data structure is inconsistent
                    throw new CannotPack();
                }

                packedValue = packMap(m2, nestedHeader, keyIndexNested);
            } else {
                if (header.get(keyIndexValue + 1) instanceof List) {
                    throw new CannotPack();
                }

                packedValue = pack(entry.getValue());
            }

            while (row.size() < keyIndexValue) {
                row.add(new MessagePackExtensionType(UNDEFINED_BYTE, new byte[0]));
            }

            if (row.size() == keyIndexValue) {
                row.add(packedValue);
            } else {
                row.set(keyIndexValue, packedValue);
            }
        }
        return row;
    }

    static Map<Object, Object> unpackBody(Map<Object, Object> body) {
        final var result = new HashMap<Object, Object>();

        for (final var entry : body.entrySet()) {
            final var unpackedValue = unpack(entry.getValue());
            result.put(entry.getKey(), unpackedValue);
        }

        return result;
    }

    static Object unpack(Object value) {
        if (value instanceof final List l) {
            return unpackList(l);
        } else if (value instanceof final Map<?, ?> m) {
            final var newMap = new HashMap<Object, Object>();

            for (Map.Entry<?, ?> entry : m.entrySet()) {
                newMap.put(entry.getKey(), unpack(entry.getValue()));
            }

            return newMap;
        } else {
            return value;
        }
    }

    static List<Object> unpackList(List<Object> list) {
        if (list.isEmpty()) {
            return list;
        }

        if (!(list.get(0) instanceof final MessagePackExtensionType t && t.getType() == PACKED_BYTE)) {
            final var newList = new ArrayList<Object>();
            for (final var e : list) {
                newList.add(unpack(e));
            }
            return newList;
        }

        final var unpackedList = new ArrayList<Object>();
        final var headers = (List<Object>) list.get(1);

        for (int i = 2; i < list.size(); i += 1) {
            final var row = (List<Object>) list.get(i);
            final var m = unpackMap(row, headers);

            unpackedList.add(m);
        }

        return unpackedList;
    }

    static Map<Integer, Object> unpackMap(List<Object> row, List<Object> header) {
        final var finalMap = new HashMap<Integer, Object>();

        for (int j = 0; j < row.size(); j += 1) {
            final var key = header.get(j + 1);
            final var value = row.get(j);

            if (value instanceof final MessagePackExtensionType t && t.getType() == UNDEFINED_BYTE) {
                continue;
            }

            if (key instanceof final List l) {
                final var nestedHeader = (List<Object>) l;
                final var nestedRow = (List<Object>) value;
                final var m = unpackMap(nestedRow, nestedHeader);
                final var i = (Integer) nestedHeader.get(0);

                finalMap.put(i, m);
            } else {
                final Integer i = (Integer) key;
                final var unpackedValue = unpack(value);

                finalMap.put(i, unpackedValue);
            }
        }

        return finalMap;
    }

    static List<Object> serverBinaryEncode(List<Object> message, _BinaryEncoding binaryEncoder) {
        final var headers = (Map<String, Object>) message.get(0);
        final var messageBody = (Map<String, Object>) message.get(1);
        final var clientKnownBinaryChecksums = (List<Integer>) headers.remove("_clientKnownBinaryChecksums");

        if (clientKnownBinaryChecksums == null || !clientKnownBinaryChecksums.contains(binaryEncoder.checksum)) {
            headers.put("enc_", binaryEncoder.encodeMap);
        }

        headers.put("bin_", List.of(binaryEncoder.checksum));
        final var encodedMessageBody = encodeBody(messageBody, binaryEncoder);

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("_pac"))) {
            finalEncodedMessageBody = packBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        return List.of(headers, finalEncodedMessageBody);
    }

    static List<Object> serverBinaryDecode(List<Object> message, _BinaryEncoding binaryEncoder) {
        final var headers = (Map<String, Object>) message.get(0);
        final var encodedMessageBody = (Map<Object, Object>) message.get(1);
        final var clientKnownBinaryChecksums = (List<Integer>) headers.get("bin_");
        final var binaryChecksumUsedByClientOnThisMessage = clientKnownBinaryChecksums.get(0);

        if (!Objects.equals(binaryChecksumUsedByClientOnThisMessage, binaryEncoder.checksum)) {
            throw new _BinaryEncoderUnavailableError();
        }

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("_pac"))) {
            finalEncodedMessageBody = unpackBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        final var messageBody = (Map<String, Object>) decodeBody(finalEncodedMessageBody, binaryEncoder);
        return List.of(headers, messageBody);
    }

    static List<Object> clientBinaryEncode(List<Object> message, Map<Integer, _BinaryEncoding> recentBinaryEncoders,
            ClientBinaryStrategy binaryChecksumStrategy)
            throws _BinaryEncoderUnavailableError {
        final var headers = (Map<String, Object>) message.get(0);
        final var messageBody = (Map<String, Object>) message.get(1);
        final var forceSendJson = headers.remove("_forceSendJson");

        headers.put("bin_", binaryChecksumStrategy.getCurrentChecksums());

        if (Objects.equals(forceSendJson, true)) {
            throw new _BinaryEncoderUnavailableError();
        }

        if (recentBinaryEncoders.size() > 1) {
            throw new _BinaryEncoderUnavailableError();
        }

        final Optional<_BinaryEncoding> binaryEncoderOptional = recentBinaryEncoders.values().stream().findAny();
        if (!binaryEncoderOptional.isPresent()) {
            throw new _BinaryEncoderUnavailableError();
        }
        final _BinaryEncoding binaryEncoder = binaryEncoderOptional.get();

        final var encodedMessageBody = encodeBody(messageBody, binaryEncoder);

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("_pac"))) {
            finalEncodedMessageBody = packBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        return List.of(headers, finalEncodedMessageBody);
    }

    static List<Object> clientBinaryDecode(List<Object> message, Map<Integer, _BinaryEncoding> recentBinaryEncoders,
            ClientBinaryStrategy binaryChecksumStrategy)
            throws _BinaryEncoderUnavailableError {
        final var headers = (Map<String, Object>) message.get(0);
        final var encodedMessageBody = (Map<Object, Object>) message.get(1);
        final var binaryChecksums = (List<Integer>) headers.get("bin_");
        final var binaryChecksum = binaryChecksums.get(0);

        // If there is a binary encoding included on this message, cache it
        if (headers.containsKey("enc_")) {
            final var binaryEncoding = (Map<String, Integer>) headers.get("enc_");
            final var newBinaryEncoder = new _BinaryEncoding(binaryEncoding, binaryChecksum);

            recentBinaryEncoders.put(binaryChecksum, newBinaryEncoder);
        }

        binaryChecksumStrategy.update(binaryChecksum);
        final var newCurrentChecksumStrategy = binaryChecksumStrategy.getCurrentChecksums();

        recentBinaryEncoders.entrySet().removeIf(e -> !newCurrentChecksumStrategy.contains(e.getKey()));
        final var binaryEncoder = recentBinaryEncoders.get(binaryChecksum);

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("_pac"))) {
            finalEncodedMessageBody = unpackBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        final var messageBody = decodeBody(finalEncodedMessageBody, binaryEncoder);
        return List.of(headers, messageBody);
    }

    private static Map<Object, Object> encodeBody(Map<String, Object> messageBody, _BinaryEncoding binaryEncoder) {
        return (Map<Object, Object>) encodeKeys(messageBody, binaryEncoder);
    }

    static Map<String, Object> decodeBody(Map<Object, Object> encodedMessageBody, _BinaryEncoding binaryEncoder) {
        return (Map<String, Object>) decodeKeys(encodedMessageBody, binaryEncoder);
    }

    private static Object encodeKeys(Object given, _BinaryEncoding binaryEncoder) {
        if (given == null) {
            return given;
        } else if (given instanceof final Map<?, ?> m) {
            final var newMap = new HashMap<Object, Object>();

            for (final var e : m.entrySet()) {
                final var key = e.getKey();

                final Object finalKey;
                if (binaryEncoder.encodeMap.containsKey(key)) {
                    finalKey = binaryEncoder.encodeMap.get(key);
                } else {
                    finalKey = key;
                }

                final var encodedValue = encodeKeys(e.getValue(), binaryEncoder);

                newMap.put(finalKey, encodedValue);
            }

            return newMap;
        } else if (given instanceof List<?> l) {
            return l.stream().map(e -> encodeKeys(e, binaryEncoder)).toList();
        } else {
            return given;
        }
    }

    private static Object decodeKeys(Object given, _BinaryEncoding binaryEncoder) {
        if (given instanceof Map<?, ?> m) {
            final var newMap = new HashMap<String, Object>();

            for (final var e : m.entrySet()) {
                final String key;
                if (e.getKey() instanceof final String s) {
                    key = s;
                } else {
                    key = (String) binaryEncoder.decodeMap.get(e.getKey());

                    if (key == null) {
                        throw new _BinaryEncodingMissing(key);
                    }
                }
                final var encodedValue = decodeKeys(e.getValue(), binaryEncoder);

                newMap.put(key, encodedValue);
            }

            return newMap;
        } else if (given instanceof final List<?> l) {
            return l.stream().map(e -> decodeKeys(e, binaryEncoder)).toList();
        } else {
            return given;
        }
    }

    static _BinaryEncoding constructBinaryEncoding(UApiSchema uApiSchema) {
        final var allKeys = new TreeSet<String>();
        for (final var entry : uApiSchema.parsed.entrySet()) {
            allKeys.add(entry.getKey());

            if (entry.getValue() instanceof final _UStruct s) {
                final Map<String, _UFieldDeclaration> structFields = s.fields;
                allKeys.addAll(structFields.keySet());
            } else if (entry.getValue() instanceof final _UUnion u) {
                final Map<String, _UStruct> unionCases = u.cases;
                for (final var entry2 : unionCases.entrySet()) {
                    allKeys.add(entry2.getKey());
                    final var struct = entry2.getValue();
                    final var structFields = struct.fields;
                    allKeys.addAll(structFields.keySet());
                }
            } else if (entry.getValue() instanceof final _UFn f) {
                final _UUnion fnCall = f.call;
                final Map<String, _UStruct> fnCallCases = fnCall.cases;
                final _UUnion fnResult = f.result;
                final Map<String, _UStruct> fnResultCases = fnResult.cases;

                for (final var e2 : fnCallCases.entrySet()) {
                    allKeys.add(e2.getKey());
                    final var struct = e2.getValue();
                    final Map<String, _UFieldDeclaration> structFields = struct.fields;
                    allKeys.addAll(structFields.keySet());
                }

                for (var e2 : fnResultCases.entrySet()) {
                    allKeys.add(e2.getKey());
                    var struct = e2.getValue();
                    final Map<String, _UFieldDeclaration> structFields = struct.fields;
                    allKeys.addAll(structFields.keySet());
                }
            }
        }
        var i = 0;
        final var binaryEncodingMap = new HashMap<String, Integer>();
        for (final var key : allKeys) {
            binaryEncodingMap.put(key, i);
            i += 1;
        }
        final var finalString = String.join("\n", allKeys);

        final int checksum = createChecksum(finalString);
        return new _BinaryEncoding(binaryEncodingMap, checksum);
    }

    static int createChecksum(String value) {
        var c = new CRC32();
        c.update(value.getBytes(StandardCharsets.UTF_8));
        return (int) c.getValue();
    }

    static byte[] serialize(Message message, _BinaryEncoder binaryEncoder,
            SerializationImpl serializer) {
        final var headers = message.header;

        final boolean serializeAsBinary;
        if (headers.containsKey("_binary")) {
            serializeAsBinary = Objects.equals(true, headers.remove("_binary"));
        } else {
            serializeAsBinary = false;
        }

        final List<Object> messageAsPseudoJson = List.of(message.header, message.body);

        try {
            if (serializeAsBinary) {
                try {
                    final var encodedMessage = binaryEncoder.encode(messageAsPseudoJson);
                    return serializer.toMsgPack(encodedMessage);
                } catch (_BinaryEncoderUnavailableError e) {
                    // We can still submit as json
                    return serializer.toJson(messageAsPseudoJson);
                }
            } else {
                return serializer.toJson(messageAsPseudoJson);
            }
        } catch (Throwable e) {
            throw new SerializationError(e);
        }
    }

    static Message deserialize(byte[] messageBytes, SerializationImpl serializer,
            _BinaryEncoder binaryEncoder) {
        final Object messageAsPseudoJson;
        final boolean isMsgPack;

        try {
            if (messageBytes[0] == (byte) 0x92) { // MsgPack
                isMsgPack = true;
                messageAsPseudoJson = serializer.fromMsgPack(messageBytes);
            } else {
                isMsgPack = false;
                messageAsPseudoJson = serializer.fromJson(messageBytes);
            }
        } catch (Throwable e) {
            throw new _InvalidMessage(e);
        }

        final List<Object> messageAsPseudoJsonList;
        try {
            messageAsPseudoJsonList = asList(messageAsPseudoJson);
        } catch (ClassCastException e) {
            throw new _InvalidMessage();
        }

        if (messageAsPseudoJsonList.size() != 2) {
            throw new _InvalidMessage();
        }

        final List<Object> finalMessageAsPseudoJsonList;
        if (isMsgPack) {
            finalMessageAsPseudoJsonList = binaryEncoder.decode(messageAsPseudoJsonList);
        } else {
            finalMessageAsPseudoJsonList = messageAsPseudoJsonList;
        }

        Map<String, Object> headers = null;
        Map<String, Object> body = null;

        try {
            headers = asMap(finalMessageAsPseudoJsonList.get(0));
        } catch (ClassCastException e) {
            throw new _InvalidMessage();
        }

        try {
            body = asMap(finalMessageAsPseudoJsonList.get(1));
            if (body.size() != 1) {
                throw new _InvalidMessageBody();
            } else {
                try {
                    var givenPayload = asMap(body.values().stream().findAny().get());
                } catch (ClassCastException e) {
                    throw new _InvalidMessageBody();
                }
            }
        } catch (ClassCastException e) {
            throw new _InvalidMessage();
        }

        return new Message(headers, body);
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

    static List<_ValidationFailure> getTypeUnexpectedValidationFailure(List<Object> path, Object value,
            String expectedType) {
        final var actualType = getType(value);
        final Map<String, Object> data = new TreeMap<>(Map.ofEntries(Map.entry("actual", Map.of(actualType, Map.of())),
                Map.entry("expected", Map.of(expectedType, Map.of()))));
        return List.of(
                new _ValidationFailure(path, "TypeUnexpected", data));
    }

    static List<_ValidationFailure> validateHeaders(
            Map<String, Object> headers, Map<String, _UFieldDeclaration> parsedRequestHeaders, _UFn functionType) {
        final var validationFailures = new ArrayList<_ValidationFailure>();

        for (final var entry : headers.entrySet()) {
            final var header = entry.getKey();
            final var headerValue = entry.getValue();
            final var field = parsedRequestHeaders.get(header);
            if (field != null) {
                final var thisValidationFailures = field.typeDeclaration.validate(headerValue, null, functionType.name,
                        List.of());
                final var thisValidationFailuresPath = thisValidationFailures.stream()
                        .map(e -> new _ValidationFailure(prepend(header, e.path), e.reason, e.data)).toList();
                validationFailures.addAll(thisValidationFailuresPath);
            }
        }

        return validationFailures;
    }

    static List<_ValidationFailure> validateValueOfType(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> generics,
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
            return thisType.validate(value, select, fn, typeParameters, generics);
        }
    }

    static Object generateRandomValueOfType(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator, _UType thisType, boolean nullable,
            List<_UTypeDeclaration> typeParameters) {
        if (nullable && !useBlueprintValue && randomGenerator.nextBoolean()) {
            return null;
        } else {
            return thisType.generateRandomValue(blueprintValue, useBlueprintValue, includeOptionalFields,
                    randomizeOptionalFields,
                    typeParameters, generics, randomGenerator);
        }
    }

    static Object generateRandomAny(_RandomGenerator randomGenerator) {
        final var selectType = randomGenerator.nextIntWithCeiling(3);
        if (selectType == 0) {
            return randomGenerator.nextBoolean();
        } else if (selectType == 1) {
            return randomGenerator.nextInt();
        } else {
            return randomGenerator.nextString();
        }
    }

    static List<_ValidationFailure> validateBoolean(Object value) {
        if (value instanceof Boolean) {
            return List.of();
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _BOOLEAN_NAME);
        }
    }

    static Object generateRandomBoolean(Object blueprintValue, boolean useBlueprintValue,
            _RandomGenerator randomGenerator) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return randomGenerator.nextBoolean();
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

    static Object generateRandomInteger(Object blueprintValue, boolean useBlueprintValue,
            _RandomGenerator randomGenerator) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return randomGenerator.nextInt();
        }
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

    static Object generateRandomNumber(Object blueprintValue, boolean useBlueprintValue,
            _RandomGenerator randomGenerator) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return randomGenerator.nextDouble();
        }
    }

    static List<_ValidationFailure> validateString(Object value) {
        if (value instanceof String) {
            return List.of();
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _STRING_NAME);
        }
    }

    static Object generateRandomString(Object blueprintValue, boolean useBlueprintValue,
            _RandomGenerator randomGenerator) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return randomGenerator.nextString();
        }
    }

    static List<_ValidationFailure> validateArray(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        if (value instanceof final List l) {
            final var nestedTypeDeclaration = typeParameters.get(0);

            final var validationFailures = new ArrayList<_ValidationFailure>();
            for (var i = 0; i < l.size(); i += 1) {
                final var element = l.get(i);
                final var nestedValidationFailures = nestedTypeDeclaration.validate(element, select, fn, generics);
                final var index = i;

                final var nestedValidationFailuresWithPath = new ArrayList<_ValidationFailure>();
                for (var f : nestedValidationFailures) {
                    final List<Object> finalPath = prepend(index, f.path);
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

    static Object generateRandomArray(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        final var nestedTypeDeclaration = typeParameters.get(0);

        if (useBlueprintValue) {
            final var startingArray = (List<Object>) blueprintValue;

            final var array = new ArrayList<Object>();
            for (final var startingArrayValue : startingArray) {
                final var value = nestedTypeDeclaration.generateRandomValue(startingArrayValue, true,
                        includeOptionalFields, randomizeOptionalFields, generics, randomGenerator);

                array.add(value);
            }

            return array;
        } else {
            final var length = randomGenerator.nextCollectionLength();

            final var array = new ArrayList<Object>();
            for (int i = 0; i < length; i += 1) {
                final var value = nestedTypeDeclaration.generateRandomValue(null, false,
                        includeOptionalFields, randomizeOptionalFields,
                        generics, randomGenerator);

                array.add(value);
            }

            return array;
        }
    }

    static List<_ValidationFailure> validateObject(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        if (value instanceof final Map<?, ?> m) {
            final var nestedTypeDeclaration = typeParameters.get(0);

            final var validationFailures = new ArrayList<_ValidationFailure>();
            for (Map.Entry<?, ?> entry : m.entrySet()) {
                final var k = (String) entry.getKey();
                final var v = entry.getValue();
                final var nestedValidationFailures = nestedTypeDeclaration.validate(v, select, fn, generics);

                final var nestedValidationFailuresWithPath = new ArrayList<_ValidationFailure>();
                for (var f : nestedValidationFailures) {
                    final List<Object> thisPath = prepend(k, f.path);

                    nestedValidationFailuresWithPath.add(new _ValidationFailure(thisPath, f.reason, f.data));
                }

                validationFailures.addAll(nestedValidationFailuresWithPath);
            }

            return validationFailures;
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _OBJECT_NAME);
        }
    }

    static Object generateRandomObject(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator) {
        final var nestedTypeDeclaration = typeParameters.get(0);

        if (useBlueprintValue) {
            final var startingObj = (Map<String, Object>) blueprintValue;

            final var obj = new TreeMap<String, Object>();
            for (final var startingObjEntry : startingObj.entrySet()) {
                final var key = startingObjEntry.getKey();
                final var startingObjValue = startingObjEntry.getValue();
                final var value = nestedTypeDeclaration.generateRandomValue(startingObjValue, true,
                        includeOptionalFields, randomizeOptionalFields, generics, randomGenerator);
                obj.put(key, value);
            }

            return obj;
        } else {
            final var length = randomGenerator.nextCollectionLength();

            final var obj = new TreeMap<String, Object>();
            for (int i = 0; i < length; i += 1) {
                final var key = randomGenerator.nextString();
                final var value = nestedTypeDeclaration.generateRandomValue(null, false, includeOptionalFields,
                        randomizeOptionalFields,
                        generics, randomGenerator);
                obj.put(key, value);
            }

            return obj;
        }
    }

    static List<_ValidationFailure> validateStruct(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, String name, Map<String, _UFieldDeclaration> fields) {
        if (value instanceof Map<?, ?> m) {
            final var selectedFields = select == null ? null : (List<String>) select.get(name);
            return validateStructFields(fields, selectedFields, (Map<String, Object>) m, select, fn, typeParameters);
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _STRUCT_NAME);
        }
    }

    static List<_ValidationFailure> validateStructFields(
            Map<String, _UFieldDeclaration> fields,
            List<String> selectedFields,
            Map<String, Object> actualStruct, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters) {
        final var validationFailures = new ArrayList<_ValidationFailure>();

        final var missingFields = new ArrayList<String>();
        for (final var entry : fields.entrySet()) {
            final var fieldName = entry.getKey();
            final var fieldDeclaration = entry.getValue();
            final boolean isOptional = fieldDeclaration.optional;
            final boolean isOmittedBySelect = selectedFields != null && !selectedFields.contains(fieldName);
            if (!actualStruct.containsKey(fieldName) && !isOptional && !isOmittedBySelect) {
                missingFields.add(fieldName);
            }
        }

        for (final var missingField : missingFields) {
            final var validationFailure = new _ValidationFailure(List.of(missingField),
                    "RequiredObjectKeyMissing",
                    Map.of());

            validationFailures.add(validationFailure);
        }

        for (final var entry : actualStruct.entrySet()) {
            final var fieldName = entry.getKey();
            final var fieldValue = entry.getValue();

            final var referenceField = fields.get(fieldName);
            if (referenceField == null) {
                var validationFailure = new _ValidationFailure(List.of(fieldName), "ObjectKeyDisallowed",
                        Map.of());

                validationFailures.add(validationFailure);
                continue;
            }

            final _UTypeDeclaration refFieldTypeDeclaration = referenceField.typeDeclaration;

            final var nestedValidationFailures = refFieldTypeDeclaration.validate(fieldValue, select, fn,
                    typeParameters);

            final var nestedValidationFailuresWithPath = new ArrayList<_ValidationFailure>();
            for (final var f : nestedValidationFailures) {
                final List<Object> thisPath = prepend(fieldName, f.path);

                nestedValidationFailuresWithPath.add(new _ValidationFailure(thisPath, f.reason, f.data));
            }

            validationFailures.addAll(nestedValidationFailuresWithPath);
        }

        return validationFailures;
    }

    static Object generateRandomStruct(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator,
            Map<String, _UFieldDeclaration> fields) {
        if (useBlueprintValue) {
            final var startingStructValue = (Map<String, Object>) blueprintValue;
            return constructRandomStruct(fields, startingStructValue, includeOptionalFields, randomizeOptionalFields,
                    typeParameters, randomGenerator);
        } else {
            return constructRandomStruct(fields, new HashMap<>(), includeOptionalFields, randomizeOptionalFields,
                    typeParameters, randomGenerator);
        }
    }

    static Map<String, Object> constructRandomStruct(
            Map<String, _UFieldDeclaration> referenceStruct, Map<String, Object> startingStruct,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            _RandomGenerator randomGenerator) {

        final var sortedReferenceStruct = new ArrayList<>(referenceStruct.entrySet());
        Collections.sort(sortedReferenceStruct, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

        final var obj = new TreeMap<String, Object>();
        for (final var field : sortedReferenceStruct) {
            final var fieldName = field.getKey();
            final var fieldDeclaration = field.getValue();
            final var blueprintValue = startingStruct.get(fieldName);
            final var useBlueprintValue = startingStruct.containsKey(fieldName);
            final _UTypeDeclaration typeDeclaration = fieldDeclaration.typeDeclaration;

            final Object value;
            if (useBlueprintValue) {
                value = typeDeclaration.generateRandomValue(blueprintValue, useBlueprintValue,
                        includeOptionalFields, randomizeOptionalFields, typeParameters, randomGenerator);
            } else {
                if (!fieldDeclaration.optional) {
                    value = typeDeclaration.generateRandomValue(null, false,
                            includeOptionalFields, randomizeOptionalFields, typeParameters, randomGenerator);
                } else {
                    if (!includeOptionalFields || (randomizeOptionalFields && randomGenerator.nextBoolean())) {
                        continue;
                    }
                    value = typeDeclaration.generateRandomValue(null, false,
                            includeOptionalFields, randomizeOptionalFields, typeParameters, randomGenerator);
                }
            }

            obj.put(fieldName, value);
        }
        return obj;
    }

    static Map.Entry<String, Object> unionEntry(Map<String, Object> union) {
        return union.entrySet().stream().findAny().orElse(null);
    }

    static List<_ValidationFailure> validateUnion(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, String name, Map<String, _UStruct> cases) {
        if (value instanceof Map<?, ?> m) {
            Map<String, Object> selectedCases;
            if (name.startsWith("fn.")) {
                selectedCases = new HashMap<>();
                selectedCases.put(name, select == null ? null : select.get(name));
            } else {
                selectedCases = select == null ? null : (Map<String, Object>) select.get(name);
            }
            return validateUnionCases(cases, selectedCases, m, select, fn, typeParameters);
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _UNION_NAME);
        }
    }

    private static List<_ValidationFailure> validateUnionCases(
            Map<String, _UStruct> referenceCases, Map<String, Object> selectedCases,
            Map<?, ?> actual, Map<String, Object> select, String fn, List<_UTypeDeclaration> typeParameters) {
        if (actual.size() != 1) {
            return List.of(
                    new _ValidationFailure(new ArrayList<Object>(),
                            "ObjectSizeUnexpected", Map.of("actual", actual.size(), "expected", 1)));
        }

        final var entry = unionEntry((Map<String, Object>) actual);
        final var unionTarget = (String) entry.getKey();
        final var unionPayload = entry.getValue();

        final var referenceStruct = referenceCases.get(unionTarget);
        if (referenceStruct == null) {
            return Collections
                    .singletonList(new _ValidationFailure(List.of(unionTarget),
                            "ObjectKeyDisallowed", Map.of()));
        }

        if (unionPayload instanceof Map<?, ?> m2) {
            final var nestedValidationFailures = validateUnionStruct(referenceStruct, unionTarget,
                    (Map<String, Object>) m2, selectedCases, select, fn, typeParameters);

            final var nestedValidationFailuresWithPath = new ArrayList<_ValidationFailure>();
            for (final var f : nestedValidationFailures) {
                final List<Object> thisPath = prepend(unionTarget, f.path);

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
            Map<String, Object> actual, Map<String, Object> selectedCases, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters) {
        final var selectedFields = selectedCases == null ? null : (List<String>) selectedCases.get(unionCase);
        return validateStructFields(unionStruct.fields, selectedFields, actual, select, fn, typeParameters);
    }

    static Object generateRandomUnion(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator, Map<String, _UStruct> cases) {
        if (useBlueprintValue) {
            final var startingUnionCase = (Map<String, Object>) blueprintValue;
            return constructRandomUnion(cases, startingUnionCase, includeOptionalFields, randomizeOptionalFields,
                    typeParameters, randomGenerator);
        } else {
            return constructRandomUnion(cases, new HashMap<>(), includeOptionalFields, randomizeOptionalFields,
                    typeParameters, randomGenerator);
        }
    }

    static Map<String, Object> constructRandomUnion(Map<String, _UStruct> unionCasesReference,
            Map<String, Object> startingUnion,
            boolean includeOptionalFields, boolean randomizeOptionalFields,
            List<_UTypeDeclaration> typeParameters,
            _RandomGenerator randomGenerator) {
        if (!startingUnion.isEmpty()) {
            final var entry = unionEntry(startingUnion);
            final var unionCase = entry.getKey();
            final var unionStructType = unionCasesReference.get(unionCase);
            final var unionStartingStruct = (Map<String, Object>) startingUnion.get(unionCase);

            return Map.of(unionCase, constructRandomStruct(unionStructType.fields, unionStartingStruct,
                    includeOptionalFields, randomizeOptionalFields, typeParameters, randomGenerator));
        } else {
            final var sortedUnionCasesReference = new ArrayList<>(unionCasesReference.entrySet());

            Collections.sort(sortedUnionCasesReference, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

            final var randomIndex = randomGenerator.nextIntWithCeiling(sortedUnionCasesReference.size() - 1);
            final var unionEntry = sortedUnionCasesReference.get(randomIndex);
            final var unionCase = unionEntry.getKey();
            final var unionData = unionEntry.getValue();

            return Map.of(unionCase,
                    constructRandomStruct(unionData.fields, new HashMap<>(), includeOptionalFields,
                            randomizeOptionalFields,
                            typeParameters, randomGenerator));
        }
    }

    static Object generateRandomFn(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator, Map<String, _UStruct> callCases) {
        if (useBlueprintValue) {
            final var startingFnValue = (Map<String, Object>) blueprintValue;
            return constructRandomUnion(callCases, startingFnValue, includeOptionalFields, randomizeOptionalFields,
                    List.of(), randomGenerator);
        } else {
            return constructRandomUnion(callCases, new HashMap<>(), includeOptionalFields, randomizeOptionalFields,
                    List.of(), randomGenerator);
        }
    }

    static List<_ValidationFailure> validateSelect(Object givenObj, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, Map<String, _UType> types) {
        Map<String, Object> selectStructFieldsHeader;
        try {
            selectStructFieldsHeader = asMap(givenObj);
        } catch (ClassCastException e) {
            return getTypeUnexpectedValidationFailure(List.of(),
                    givenObj, "Object");
        }

        final var validationFailures = new ArrayList<_ValidationFailure>();
        final var functionType = (_UFn) types.get(fn);

        for (final var entry : selectStructFieldsHeader.entrySet()) {
            final var typeName = entry.getKey();
            final var selectValue = entry.getValue();

            final _UType typeReference;
            if (typeName.equals("->")) {
                typeReference = functionType.result;
            } else {
                typeReference = types.get(typeName);
            }

            if (typeReference == null) {
                validationFailures.add(new _ValidationFailure(List.of(typeName),
                        "ObjectKeyDisallowed", Map.of()));
                continue;
            }

            if (typeReference instanceof final _UUnion u) {
                final Map<String, Object> unionCases;
                try {
                    unionCases = asMap(selectValue);
                } catch (ClassCastException e) {
                    validationFailures.addAll(
                            getTypeUnexpectedValidationFailure(List.of(typeName), selectValue, "Object"));
                    continue;
                }

                for (final var unionCaseEntry : unionCases.entrySet()) {
                    final var unionCase = unionCaseEntry.getKey();
                    final var selectedCaseStructFields = unionCaseEntry.getValue();
                    final var structRef = u.cases.get(unionCase);

                    final List<Object> loopPath = List.of(typeName, unionCase);

                    if (structRef == null) {
                        validationFailures.add(new _ValidationFailure(
                                loopPath,
                                "ObjectKeyDisallowed", Map.of()));
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
                final var nestedValidationFailures = validateSelectStruct(argStruct, List.of(typeName),
                        selectValue);

                validationFailures.addAll(nestedValidationFailures);
            } else {
                final var structRef = (_UStruct) typeReference;
                final var nestedValidationFailures = validateSelectStruct(structRef, List.of(typeName),
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
            fields = asList(selectedFields);
        } catch (ClassCastException e) {
            return getTypeUnexpectedValidationFailure(basePath, selectedFields, "Array");
        }

        for (int i = 0; i < fields.size(); i += 1) {
            var field = fields.get(i);
            String stringField;
            try {
                stringField = asString(field);
            } catch (ClassCastException e) {
                final List<Object> thisPath = append(basePath, i);

                validationFailures.addAll(getTypeUnexpectedValidationFailure(thisPath, field, "String"));
                continue;
            }
            if (!structReference.fields.containsKey(stringField)) {
                final List<Object> thisPath = append(basePath, i);

                validationFailures.add(new _ValidationFailure(thisPath, "ObjectKeyDisallowed", Map.of()));
            }
        }

        return validationFailures;
    }

    static List<_ValidationFailure> validateMockCall(Object givenObj, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, Map<String, _UType> types) {
        final Map<String, Object> givenMap;
        try {
            givenMap = asMap(givenObj);
        } catch (ClassCastException e) {
            return getTypeUnexpectedValidationFailure(new ArrayList<Object>(), givenObj, "Object");
        }

        final var regexString = "^fn\\..*$";

        final var keys = givenMap.keySet().stream().sorted().toList();

        final var matches = keys.stream().filter(k -> k.matches(regexString)).toList();
        if (matches.size() != 1) {
            return List.of(new _ValidationFailure(new ArrayList<Object>(), "ObjectKeyRegexMatchCountUnexpected",
                    Map.of("regex", regexString, "actual", matches.size(), "expected", 1, "keys", keys)));
        }

        final var functionName = matches.get(0);
        final var functionDef = (_UFn) types.get(functionName);
        final var input = givenMap.get(functionName);

        final _UUnion functionDefCall = functionDef.call;
        final String functionDefName = functionDef.name;
        final Map<String, _UStruct> functionDefCallCases = functionDefCall.cases;

        final var inputFailures = functionDefCallCases.get(functionDefName).validate(input, select, fn, List.of(),
                List.of());

        final var inputFailuresWithPath = new ArrayList<_ValidationFailure>();
        for (var f : inputFailures) {
            List<Object> newPath = prepend(functionName, f.path);

            inputFailuresWithPath.add(new _ValidationFailure(newPath, f.reason, f.data));
        }

        return inputFailuresWithPath.stream()
                .filter(f -> !f.reason.equals("RequiredObjectKeyMissing")).toList();
    }

    static List<_ValidationFailure> validateMockStub(Object givenObj, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, Map<String, _UType> types) {
        final var validationFailures = new ArrayList<_ValidationFailure>();

        final Map<String, Object> givenMap;
        try {
            givenMap = asMap(givenObj);
        } catch (ClassCastException e) {
            return getTypeUnexpectedValidationFailure(List.of(), givenObj, "Object");
        }

        final var regexString = "^fn\\..*$";

        final var keys = givenMap.keySet().stream().sorted().toList();

        final var matches = keys.stream().filter(k -> k.matches(regexString)).toList();
        if (matches.size() != 1) {
            return List.of(
                    new _ValidationFailure(List.of(),
                            "ObjectKeyRegexMatchCountUnexpected",
                            Map.of("regex", regexString, "actual",
                                    matches.size(), "expected", 1, "keys", keys)));

        }

        final var functionName = matches.get(0);
        final var functionDef = (_UFn) types.get(functionName);
        final var input = givenMap.get(functionName);

        final _UUnion functionDefCall = functionDef.call;
        final String functionDefName = functionDef.name;
        final Map<String, _UStruct> functionDefCallCases = functionDefCall.cases;
        final var inputFailures = functionDefCallCases.get(functionDefName).validate(input, select, fn, List.of(),
                List.of());

        final var inputFailuresWithPath = new ArrayList<_ValidationFailure>();
        for (final var f : inputFailures) {
            final List<Object> thisPath = prepend(functionName, f.path);

            inputFailuresWithPath.add(new _ValidationFailure(thisPath, f.reason, f.data));
        }

        final var inputFailuresWithoutMissingRequired = inputFailuresWithPath.stream()
                .filter(f -> !Objects.equals(f.reason, "RequiredObjectKeyMissing")).toList();

        validationFailures.addAll(inputFailuresWithoutMissingRequired);

        final var resultDefKey = "->";

        if (!givenMap.containsKey(resultDefKey)) {
            validationFailures.add(new _ValidationFailure(List.of(resultDefKey),
                    "RequiredObjectKeyMissing",
                    Map.of()));
        } else {
            final var output = givenMap.get(resultDefKey);
            final var outputFailures = functionDef.result.validate(output, select, fn, List.of(), List.of());

            final var outputFailuresWithPath = new ArrayList<_ValidationFailure>();
            for (final var f : outputFailures) {
                final List<Object> thisPath = prepend(resultDefKey, f.path);

                outputFailuresWithPath.add(new _ValidationFailure(thisPath, f.reason, f.data));
            }

            final var failuresWithoutMissingRequired = outputFailuresWithPath
                    .stream()
                    .filter(f -> !Objects.equals(f.reason, "RequiredObjectKeyMissing"))
                    .toList();

            validationFailures.addAll(failuresWithoutMissingRequired);
        }

        final var disallowedFields = givenMap.keySet().stream()
                .filter(k -> !matches.contains(k) && !Objects.equals(k, resultDefKey)).toList();
        for (final var disallowedField : disallowedFields) {
            validationFailures
                    .add(new _ValidationFailure(List.of(disallowedField), "ObjectKeyDisallowed", Map.of()));
        }

        return validationFailures;
    }

    static Object selectStructFields(_UTypeDeclaration typeDeclaration, Object value,
            Map<String, Object> selectedStructFields) {
        final _UType typeDeclarationType = typeDeclaration.type;
        final List<_UTypeDeclaration> typeDeclarationTypeParams = typeDeclaration.typeParameters;

        if (typeDeclarationType instanceof final _UStruct s) {
            final Map<String, _UFieldDeclaration> fields = s.fields;
            final String structName = s.name;
            final var selectedFields = (List<String>) selectedStructFields.get(structName);
            final var valueAsMap = (Map<String, Object>) value;
            final var finalMap = new HashMap<>();

            for (final var entry : valueAsMap.entrySet()) {
                final var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    final var field = fields.get(fieldName);
                    final _UTypeDeclaration fieldTypeDeclaration = field.typeDeclaration;
                    final var valueWithSelectedFields = selectStructFields(fieldTypeDeclaration, entry.getValue(),
                            selectedStructFields);

                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }

            return finalMap;
        } else if (typeDeclarationType instanceof final _UFn f) {
            final var valueAsMap = (Map<String, Object>) value;
            final Map.Entry<String, Object> uEntry = unionEntry(valueAsMap);
            final var unionCase = uEntry.getKey();
            final var unionData = (Map<String, Object>) uEntry.getValue();

            final String fnName = f.name;
            final _UUnion fnCall = f.call;
            final Map<String, _UStruct> fnCallCases = fnCall.cases;

            final var argStructReference = fnCallCases.get(unionCase);
            final var selectedFields = (List<String>) selectedStructFields.get(fnName);
            final var finalMap = new HashMap<>();

            for (final var entry : unionData.entrySet()) {
                final var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    final var field = argStructReference.fields.get(fieldName);
                    final var valueWithSelectedFields = selectStructFields(field.typeDeclaration, entry.getValue(),
                            selectedStructFields);

                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }

            return Map.of(uEntry.getKey(), finalMap);
        } else if (typeDeclarationType instanceof final _UUnion u) {
            final var valueAsMap = (Map<String, Object>) value;
            final var uEntry = unionEntry(valueAsMap);
            final var unionCase = uEntry.getKey();
            final var unionData = (Map<String, Object>) uEntry.getValue();

            final Map<String, _UStruct> unionCases = u.cases;
            final var unionStructReference = unionCases.get(unionCase);
            final var unionStructRefFields = unionStructReference.fields;
            final var defaultCasesToFields = new HashMap<String, List<String>>();

            for (final var entry : unionCases.entrySet()) {
                final var unionStruct = entry.getValue();
                final var unionStructFields = unionStruct.fields;
                final var fields = unionStructFields.keySet().stream().toList();
                defaultCasesToFields.put(entry.getKey(), fields);
            }

            final var unionSelectedFields = (Map<String, Object>) selectedStructFields.getOrDefault(u.name,
                    defaultCasesToFields);
            final var thisUnionCaseSelectedFieldsDefault = defaultCasesToFields.get(unionCase);
            final var selectedFields = (List<String>) unionSelectedFields.getOrDefault(unionCase,
                    thisUnionCaseSelectedFieldsDefault);

            final var finalMap = new HashMap<>();
            for (final var entry : unionData.entrySet()) {
                final var fieldName = entry.getKey();
                if (selectedFields == null || selectedFields.contains(fieldName)) {
                    final var field = unionStructRefFields.get(fieldName);
                    final var valueWithSelectedFields = selectStructFields(field.typeDeclaration, entry.getValue(),
                            selectedStructFields);
                    finalMap.put(entry.getKey(), valueWithSelectedFields);
                }
            }

            return Map.of(uEntry.getKey(), finalMap);
        } else if (typeDeclarationType instanceof final _UObject o) {
            final var nestedTypeDeclaration = typeDeclarationTypeParams.get(0);
            final var valueAsMap = (Map<String, Object>) value;

            final var finalMap = new HashMap<>();
            for (final var entry : valueAsMap.entrySet()) {
                final var valueWithSelectedFields = selectStructFields(nestedTypeDeclaration, entry.getValue(),
                        selectedStructFields);
                finalMap.put(entry.getKey(), valueWithSelectedFields);
            }

            return finalMap;
        } else if (typeDeclarationType instanceof final _UArray a) {
            final var nestedType = typeDeclarationTypeParams.get(0);
            final var valueAsList = (List<Object>) value;

            final var finalList = new ArrayList<>();
            for (final var entry : valueAsList) {
                final var valueWithSelectedFields = selectStructFields(nestedType, entry, selectedStructFields);
                finalList.add(valueWithSelectedFields);
            }

            return finalList;
        } else {
            return value;
        }
    }

    private static Message getInvalidErrorMessage(String error, List<_ValidationFailure> validationFailures,
            _UUnion resultUnionType, Map<String, Object> responseHeaders) {
        final var validationFailureCases = mapValidationFailuresToInvalidFieldCases(validationFailures);
        final Map<String, Object> newErrorResult = Map.of(error,
                Map.of("cases", validationFailureCases));

        validateResult(resultUnionType, newErrorResult);
        return new Message(responseHeaders, newErrorResult);
    }

    private static List<Map<String, Object>> mapValidationFailuresToInvalidFieldCases(
            List<_ValidationFailure> argumentValidationFailures) {
        final var validationFailureCases = new ArrayList<Map<String, Object>>();
        for (final var validationFailure : argumentValidationFailures) {
            final Map<String, Object> validationFailureCase = Map.of(
                    "path", validationFailure.path,
                    "reason", Map.of(validationFailure.reason, validationFailure.data));
            validationFailureCases.add(validationFailureCase);
        }

        return validationFailureCases;
    }

    private static void validateResult(_UUnion resultUnionType, Object errorResult) {
        final var newErrorResultValidationFailures = resultUnionType.validate(
                errorResult, null, null, List.of(), List.of());
        if (!newErrorResultValidationFailures.isEmpty()) {
            throw new UApiError(
                    "Failed internal uAPI validation: "
                            + mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures));
        }
    }

    static Message handleMessage(Message requestMessage, UApiSchema uApiSchema, Function<Message, Message> handler,
            Consumer<Throwable> onError) {
        final var responseHeaders = (Map<String, Object>) new HashMap<String, Object>();
        final Map<String, Object> requestHeaders = requestMessage.header;
        final Map<String, Object> requestBody = requestMessage.body;
        final Map<String, _UType> parsedUApiSchema = uApiSchema.parsed;
        final Map.Entry<String, Object> requestEntry = unionEntry(requestBody);

        final String requestTargetInit = requestEntry.getKey();
        final Map<String, Object> requestPayload = (Map<String, Object>) requestEntry.getValue();

        final String unknownTarget;
        final String requestTarget;
        if (!parsedUApiSchema.containsKey(requestTargetInit)) {
            unknownTarget = requestTargetInit;
            requestTarget = "fn.ping_";
        } else {
            unknownTarget = null;
            requestTarget = requestTargetInit;
        }

        final var functionType = (_UFn) parsedUApiSchema.get(requestTarget);
        final var resultUnionType = functionType.result;

        final var callId = requestHeaders.get("id_");
        if (callId != null) {
            responseHeaders.put("id_", callId);
        }

        if (requestHeaders.containsKey("_parseFailures")) {
            final var parseFailures = (List<Object>) requestHeaders.get("_parseFailures");
            final Map<String, Object> newErrorResult = Map.of("ErrorParseFailure_",
                    Map.of("reasons", parseFailures));

            validateResult(resultUnionType, newErrorResult);

            return new Message(responseHeaders, newErrorResult);
        }

        final List<_ValidationFailure> requestHeaderValidationFailures = validateHeaders(requestHeaders,
                uApiSchema.parsedRequestHeaders, functionType);
        if (!requestHeaderValidationFailures.isEmpty()) {
            return getInvalidErrorMessage("ErrorInvalidRequestHeaders_", requestHeaderValidationFailures,
                    resultUnionType,
                    responseHeaders);
        }

        if (requestHeaders.containsKey("bin_")) {
            final List<Object> clientKnownBinaryChecksums = (List<Object>) requestHeaders.get("bin_");

            responseHeaders.put("_binary", true);
            responseHeaders.put("_clientKnownBinaryChecksums", clientKnownBinaryChecksums);

            if (requestHeaders.containsKey("_pac")) {
                responseHeaders.put("_pac", requestHeaders.get("_pac"));
            }
        }

        final Map<String, Object> selectStructFieldsHeader = (Map<String, Object>) requestHeaders.get("select_");

        if (unknownTarget != null) {
            final Map<String, Object> newErrorResult = Map.of("ErrorInvalidRequestBody_",
                    Map.of("cases",
                            List.of(Map.of("path", List.of(unknownTarget), "reason",
                                    Map.of("FunctionUnknown", Map.of())))));

            validateResult(resultUnionType, newErrorResult);
            return new Message(responseHeaders, newErrorResult);
        }

        final _UUnion functionTypeCall = functionType.call;

        final var callValidationFailures = functionTypeCall.validate(requestBody, null, null, List.of(), List.of());
        if (!callValidationFailures.isEmpty()) {
            return getInvalidErrorMessage("ErrorInvalidRequestBody_", callValidationFailures, resultUnionType,
                    responseHeaders);
        }

        final var unsafeResponseEnabled = Objects.equals(true, requestHeaders.get("unsafe_"));

        final var callMessage = new Message(requestHeaders, Map.of(requestTarget, requestPayload));

        final Message resultMessage;
        if (requestTarget.equals("fn.ping_")) {
            resultMessage = new Message(Map.of(), Map.of("Ok_", Map.of()));
        } else if (requestTarget.equals("fn.api_")) {
            resultMessage = new Message(Map.of(), Map.of("Ok_", Map.of("api", uApiSchema.original)));
        } else {
            try {
                resultMessage = handler.apply(callMessage);
            } catch (Throwable e) {
                try {
                    onError.accept(e);
                } catch (Throwable ignored) {

                }
                return new Message(responseHeaders, Map.of("ErrorUnknown_", Map.of()));
            }
        }

        final Map<String, Object> resultUnion = resultMessage.body;

        resultMessage.header.putAll(responseHeaders);
        final Map<String, Object> finalResponseHeaders = resultMessage.header;

        final var skipResultValidation = unsafeResponseEnabled;
        if (!skipResultValidation) {
            final var resultValidationFailures = resultUnionType.validate(
                    resultUnion, selectStructFieldsHeader, null, List.of(), List.of());
            if (!resultValidationFailures.isEmpty()) {
                return getInvalidErrorMessage("ErrorInvalidResponseBody_", resultValidationFailures, resultUnionType,
                        responseHeaders);
            }
            final List<_ValidationFailure> responseHeaderValidationFailures = validateHeaders(finalResponseHeaders,
                    uApiSchema.parsedResponseHeaders, functionType);
            if (!responseHeaderValidationFailures.isEmpty()) {
                return getInvalidErrorMessage("ErrorInvalidResponseHeaders_", responseHeaderValidationFailures,
                        resultUnionType,
                        responseHeaders);
            }
        }

        final Map<String, Object> finalResultUnion;
        if (selectStructFieldsHeader != null) {
            finalResultUnion = (Map<String, Object>) selectStructFields(
                    new _UTypeDeclaration(resultUnionType, false, List.of()),
                    resultUnion,
                    selectStructFieldsHeader);
        } else {
            finalResultUnion = resultUnion;
        }

        return new Message(finalResponseHeaders, finalResultUnion);
    }

    static Message parseRequestMessage(byte[] requestMessageBytes, Serializer serializer, UApiSchema uApiSchema,
            Consumer<Throwable> onError) {

        try {
            return serializer.deserialize(requestMessageBytes);
        } catch (Exception e) {
            onError.accept(e);

            String reason;
            if (e instanceof _BinaryEncoderUnavailableError) {
                reason = "IncompatibleBinaryEncoding";
            } else if (e instanceof _BinaryEncodingMissing) {
                reason = "BinaryDecodeFailure";
            } else if (e instanceof _InvalidMessage) {
                reason = "ExpectedJsonArrayOfTwoObjects";
            } else if (e instanceof _InvalidMessageBody) {
                reason = "ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject";
            } else {
                reason = "ExpectedJsonArrayOfTwoObjects";
            }

            return new Message(Map.of("_parseFailures", List.of(Map.of(reason, Map.of()))),
                    Map.of("_unknown", Map.of()));
        }
    }

    static byte[] processBytes(byte[] requestMessageBytes, Serializer serializer, UApiSchema uApiSchema,
            Consumer<Throwable> onError, Consumer<Message> onRequest, Consumer<Message> onResponse,
            Function<Message, Message> handler) {
        try {
            final var requestMessage = parseRequestMessage(requestMessageBytes, serializer,
                    uApiSchema, onError);

            try {
                onRequest.accept(requestMessage);
            } catch (Throwable ignored) {
            }

            final var responseMessage = handleMessage(requestMessage, uApiSchema, handler, onError);

            try {
                onResponse.accept(responseMessage);
            } catch (Throwable ignored) {
            }

            return serializer.serialize(responseMessage);
        } catch (Throwable e) {
            try {
                onError.accept(e);
            } catch (Throwable ignored) {
            }

            return serializer
                    .serialize(new Message(new HashMap<>(), Map.of("ErrorUnknown_", Map.of())));
        }
    }

    static boolean isSubMap(Map<String, Object> part, Map<String, Object> whole) {
        for (final var partKey : part.keySet()) {
            final var wholeValue = whole.get(partKey);
            final var partValue = part.get(partKey);
            final var entryIsEqual = isSubMapEntryEqual(partValue, wholeValue);
            if (!entryIsEqual) {
                return false;
            }
        }
        return true;
    }

    private static boolean isSubMapEntryEqual(Object partValue, Object wholeValue) {
        if (partValue instanceof final Map m1 && wholeValue instanceof final Map m2) {
            return isSubMap(m1, m2);
        } else if (partValue instanceof final List partList && wholeValue instanceof final List wholeList) {
            for (int i = 0; i < partList.size(); i += 1) {
                final var partElement = partList.get(i);
                final var partMatches = partiallyMatches(wholeList, partElement);
                if (!partMatches) {
                    return false;
                }
            }

            return true;
        } else {
            return Objects.equals(partValue, wholeValue);
        }
    }

    private static boolean partiallyMatches(List<Object> wholeList, Object partElement) {
        for (final var wholeElement : wholeList) {
            if (isSubMapEntryEqual(partElement, wholeElement)) {
                return true;
            }
        }

        return false;
    }

    static Map<String, Object> verify(String functionName, Map<String, Object> argument, boolean exactMatch,
            Map<String, Object> verificationTimes, List<_MockInvocation> invocations) {
        var matchesFound = 0;
        for (final var invocation : invocations) {
            if (Objects.equals(invocation.functionName, functionName)) {
                if (exactMatch) {
                    if (Objects.equals(invocation.functionArgument, argument)) {
                        invocation.verified = true;
                        matchesFound += 1;
                    }
                } else {
                    boolean isSubMap = isSubMap(argument, invocation.functionArgument);
                    if (isSubMap) {
                        invocation.verified = true;
                        matchesFound += 1;
                    }
                }
            }
        }

        final var allCallsPseudoJson = new ArrayList<Map<String, Object>>();
        for (final var invocation : invocations) {
            allCallsPseudoJson.add(Map.of(invocation.functionName, invocation.functionArgument));
        }

        final Map.Entry<String, Object> verifyTimesEntry = unionEntry(verificationTimes);
        final var verifyKey = verifyTimesEntry.getKey();
        final var verifyTimesStruct = (Map<String, Object>) verifyTimesEntry.getValue();

        Map<String, Object> verificationFailurePseudoJson = null;
        if (verifyKey.equals("Exact")) {
            final var times = (Integer) verifyTimesStruct.get("times");
            if (matchesFound > times) {
                verificationFailurePseudoJson = Map.of("TooManyMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("Exact", Map.of("times", times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));
            } else if (matchesFound < times) {
                verificationFailurePseudoJson = Map.of("TooFewMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("Exact", Map.of("times", times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));
            }
        } else if (verifyKey.equals("AtMost")) {
            final var times = (Integer) verifyTimesStruct.get("times");
            if (matchesFound > times) {
                verificationFailurePseudoJson = Map.of("TooManyMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("AtMost", Map.of("times", times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));
            }
        } else if (verifyKey.equals("AtLeast")) {
            final var times = (Integer) verifyTimesStruct.get("times");
            if (matchesFound < times) {
                verificationFailurePseudoJson = Map.of("TooFewMatchingCalls",
                        new TreeMap<>(Map.ofEntries(
                                Map.entry("wanted", Map.of("AtLeast", Map.of("times", times))),
                                Map.entry("found", matchesFound),
                                Map.entry("allCalls", allCallsPseudoJson))));

            }
        }

        if (verificationFailurePseudoJson == null) {
            return Map.of("Ok_", Map.of());
        }

        return Map.of("ErrorVerificationFailure", Map.of("reason", verificationFailurePseudoJson));
    }

    static Map<String, Object> verifyNoMoreInteractions(List<_MockInvocation> invocations) {
        final var invocationsNotVerified = invocations.stream().filter(i -> !i.verified).toList();

        if (invocationsNotVerified.size() > 0) {
            final var unverifiedCallsPseudoJson = new ArrayList<Map<String, Object>>();
            for (final var invocation : invocationsNotVerified) {
                unverifiedCallsPseudoJson.add(Map.of(invocation.functionName, invocation.functionArgument));
            }
            return Map.of("ErrorVerificationFailure",
                    Map.of("additionalUnverifiedCalls", unverifiedCallsPseudoJson));
        }

        return Map.of("Ok_", Map.of());
    }

    static Message mockHandle(Message requestMessage, List<_MockStub> stubs, List<_MockInvocation> invocations,
            _RandomGenerator random, UApiSchema uApiSchema, boolean enableGeneratedDefaultStub,
            boolean enableOptionalFieldGeneration, boolean randomizeOptionalFieldGeneration) {
        final Map<String, Object> header = requestMessage.header;

        final var enableGenerationStub = (Boolean) header.getOrDefault("_gen", false);
        final String functionName = requestMessage.getBodyTarget();
        final Map<String, Object> argument = requestMessage.getBodyPayload();

        switch (functionName) {
            case "fn.createStub_" -> {
                final var givenStub = (Map<String, Object>) argument.get("stub");

                final var stubCall = givenStub.entrySet().stream().filter(e -> e.getKey().startsWith("fn."))
                        .findAny().get();
                final var stubFunctionName = stubCall.getKey();
                final var stubArg = (Map<String, Object>) stubCall.getValue();
                final var stubResult = (Map<String, Object>) givenStub.get("->");
                final var allowArgumentPartialMatch = !((Boolean) argument.getOrDefault("strictMatch!", false));
                final var stubCount = (Integer) argument.getOrDefault("count!", -1);

                final var stub = new _MockStub(stubFunctionName, new TreeMap<>(stubArg), stubResult,
                        allowArgumentPartialMatch, stubCount);

                stubs.add(0, stub);
                return new Message(Map.of(), Map.of("Ok_", Map.of()));
            }
            case "fn.verify_" -> {
                final var givenCall = (Map<String, Object>) argument.get("call");

                final var call = givenCall.entrySet().stream().filter(e -> e.getKey().startsWith("fn."))
                        .findAny().get();
                final var callFunctionName = call.getKey();
                final var callArg = (Map<String, Object>) call.getValue();
                final var verifyTimes = (Map<String, Object>) argument.getOrDefault("count!",
                        Map.of("AtLeast", Map.of("times", 1)));
                final var strictMatch = (Boolean) argument.getOrDefault("strictMatch!", false);

                final var verificationResult = verify(callFunctionName, callArg, strictMatch,
                        verifyTimes,
                        invocations);
                return new Message(Map.of(), verificationResult);
            }
            case "fn.verifyNoMoreInteractions_" -> {
                final var verificationResult = verifyNoMoreInteractions(invocations);
                return new Message(Map.of(), verificationResult);
            }
            case "fn.clearCalls_" -> {
                invocations.clear();
                return new Message(Map.of(), Map.of("Ok_", Map.of()));
            }
            case "fn.clearStubs_" -> {
                stubs.clear();
                return new Message(Map.of(), Map.of("Ok_", Map.of()));
            }
            case "fn.setRandomSeed_" -> {
                final var givenSeed = (Integer) argument.get("seed");

                random.setSeed(givenSeed);
                return new Message(Map.of(), Map.of("Ok_", Map.of()));
            }
            default -> {
                invocations.add(new _MockInvocation(functionName, new TreeMap<>(argument)));

                final var definition = (_UFn) uApiSchema.parsed.get(functionName);

                for (final var stub : stubs) {
                    if (stub.count == 0) {
                        continue;
                    }
                    if (Objects.equals(stub.whenFunction, functionName)) {
                        if (stub.allowArgumentPartialMatch) {
                            if (isSubMap(stub.whenArgument, argument)) {
                                final var useBlueprintValue = true;
                                final var includeOptionalFields = false;
                                final var result = (Map<String, Object>) definition.result.generateRandomValue(
                                        stub.thenResult, useBlueprintValue,
                                        includeOptionalFields, randomizeOptionalFieldGeneration, List.of(), List.of(),
                                        random);
                                if (stub.count > 0) {
                                    stub.count -= 1;
                                }
                                return new Message(Map.of(), result);
                            }
                        } else {
                            if (Objects.equals(stub.whenArgument, argument)) {
                                final var useBlueprintValue = true;
                                final var includeOptionalFields = false;
                                final var result = (Map<String, Object>) definition.result.generateRandomValue(
                                        stub.thenResult, useBlueprintValue,
                                        includeOptionalFields, randomizeOptionalFieldGeneration, List.of(), List.of(),
                                        random);
                                if (stub.count > 0) {
                                    stub.count -= 1;
                                }
                                return new Message(Map.of(), result);
                            }
                        }
                    }
                }

                if (!enableGeneratedDefaultStub && !enableGenerationStub) {
                    return new Message(Map.of(), Map.of("ErrorNoMatchingStub__", Map.of()));
                }

                if (definition != null) {
                    final var resultUnion = (_UUnion) definition.result;
                    final var okStructRef = resultUnion.cases.get("Ok_");
                    final var useBlueprintValue = true;
                    final var includeOptionalFields = true;
                    final var randomOkStruct = okStructRef.generateRandomValue(new HashMap<>(), useBlueprintValue,
                            includeOptionalFields, randomizeOptionalFieldGeneration, List.of(), List.of(), random);
                    return new Message(Map.of(), Map.of("Ok_", randomOkStruct));
                } else {
                    throw new UApiError("Unexpected unknown function: %s".formatted(functionName));
                }
            }
        }
    }

    static Message processRequestObject(Message requestMessage,
            BiFunction<Message, Serializer, Future<Message>> adapter, Serializer serializer, long timeoutMsDefault,
            boolean useBinaryDefault) {
        final Map<String, Object> header = requestMessage.header;

        try {
            if (!header.containsKey("tim_")) {
                header.put("tim_", timeoutMsDefault);
            }

            if (useBinaryDefault) {
                header.put("_binary", true);
            }

            final var timeoutMs = ((Number) header.get("tim_")).longValue();

            final var responseMessage = adapter.apply(requestMessage, serializer).get(timeoutMs, TimeUnit.MILLISECONDS);

            if (Objects.equals(responseMessage.body,
                    Map.of("ErrorParseFailure_",
                            Map.of("reasons", List.of(Map.of("IncompatibleBinaryEncoding", Map.of())))))) {
                // Try again, but as json
                header.put("_binary", true);
                header.put("_forceSendJson", true);

                return adapter.apply(requestMessage, serializer).get(timeoutMs,
                        TimeUnit.MILLISECONDS);
            }

            return responseMessage;
        } catch (Exception e) {
            throw new UApiError(e);
        }
    }

    static List<Object> mapSchemaParseFailuresToPseudoJson(
            List<_SchemaParseFailure> schemaParseFailures) {
        return (List<Object>) schemaParseFailures.stream()
                .map(f -> (Object) new TreeMap<>() {
                    {
                        put("path", f.path);
                        put("reason", Map.of(f.reason, f.data));
                        if (f.key != null) {
                            put("key!", f.key);
                        }
                    }
                })
                .toList();
    }
}
