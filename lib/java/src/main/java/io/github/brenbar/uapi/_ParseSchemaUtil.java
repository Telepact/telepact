package io.github.brenbar.uapi;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.stream.Collectors;

class _ParseSchemaUtil {

    static UApiSchema newUApiSchema(String uApiSchemaJson, Map<String, _UType> typeExtensions) {
        final var objectMapper = new ObjectMapper();

        final Object uApiSchemaPseudoJsonInit;
        try {
            uApiSchemaPseudoJsonInit = objectMapper.readValue(uApiSchemaJson, new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new UApiSchemaParseError(
                    List.of(new SchemaParseFailure(List.of(), "JsonInvalid", Map.of())),
                    e);
        }

        final List<Object> uApiSchemaPseudoJson;
        try {
            uApiSchemaPseudoJson = _CastUtil.asList(uApiSchemaPseudoJsonInit);
        } catch (ClassCastException e) {
            final List<SchemaParseFailure> thisParseFailures = _ParseSchemaUtil
                    .getTypeUnexpectedValidationFailure(List.of(), uApiSchemaPseudoJsonInit, "Array");
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
                    List.of(new SchemaParseFailure(List.of(), "JsonInvalid", Map.of())),
                    e);
        }

        final List<Object> secondUApiSchemaPseudoJson;
        try {
            secondUApiSchemaPseudoJson = _CastUtil.asList(secondUApiSchemaPseudoJsonInit);
        } catch (ClassCastException e) {
            final List<SchemaParseFailure> thisParseFailure = _ParseSchemaUtil
                    .getTypeUnexpectedValidationFailure(List.of(), secondUApiSchemaPseudoJsonInit, "Array");
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
        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var failedTypes = new HashSet<String>();
        final var schemaKeysToIndex = new HashMap<String, Integer>();
        final var schemaKeys = new HashSet<String>();

        var index = -1;
        for (final var definition : uApiSchemaPseudoJson) {
            index += 1;

            final List<Object> loopPath = List.of(index);

            final Map<String, Object> def;
            try {
                def = _CastUtil.asMap(definition);
            } catch (ClassCastException e) {
                final List<SchemaParseFailure> thisParseFailures = _ParseSchemaUtil
                        .getTypeUnexpectedValidationFailure(loopPath, definition, "Object");

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

            System.out.println(schemaKeysToIndex);
            System.out.println(schemaKeys);
            System.out.println(schemaKey);
            final var matchingSchemaKey = findMatchingSchemaKey(schemaKeys, schemaKey);
            if (matchingSchemaKey != null) {
                final var otherPathIndex = schemaKeysToIndex.get(matchingSchemaKey);
                final List<Object> finalPath = _ValidateUtil.append(loopPath, schemaKey);
                System.out.print(otherPathIndex);

                parseFailures.add(new SchemaParseFailure(finalPath, "PathCollision",
                        Map.of("other", List.of(otherPathIndex, matchingSchemaKey))));
                continue;
            }

            schemaKeys.add(schemaKey);
            schemaKeysToIndex.put(schemaKey, index);
        }

        if (!parseFailures.isEmpty()) {
            final var offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset);
            throw new UApiSchemaParseError(offsetParseFailures);
        }

        final var errorKeys = new HashSet<String>();
        final var rootTypeParameterCount = 0;

        for (final var schemaKey : schemaKeys) {
            if (schemaKey.startsWith("info.")) {
                continue;
            } else if (schemaKey.startsWith("error.")) {
                errorKeys.add(schemaKey);
                continue;
            }

            final var thisIndex = schemaKeysToIndex.get(schemaKey);

            try {
                _ParseSchemaTypeUtil.getOrParseType(List.of(thisIndex), schemaKey, rootTypeParameterCount,
                        uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions, parseFailures,
                        failedTypes);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            final var offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset);
            throw new UApiSchemaParseError(offsetParseFailures);
        }

        for (final var errorKey : errorKeys) {
            final var thisIndex = schemaKeysToIndex.get(errorKey);
            final var def = (Map<String, Object>) uApiSchemaPseudoJson.get(thisIndex);

            try {
                final var error = _ParseSchemaErrorUtil.parseErrorType(def, errorKey, uApiSchemaPseudoJson,
                        schemaKeysToIndex, parsedTypes, typeExtensions, parseFailures, failedTypes);
                _ParseSchemaErrorUtil.applyErrorToParsedTypes(error, parsedTypes, schemaKeysToIndex);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            final var offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset);
            throw new UApiSchemaParseError(offsetParseFailures);
        }

        return new UApiSchema(uApiSchemaPseudoJson, parsedTypes, typeExtensions);
    }

    private static List<SchemaParseFailure> offsetSchemaIndex(List<SchemaParseFailure> initialFailures, int offset) {
        final var finalList = new ArrayList<SchemaParseFailure>();

        for (final var f : initialFailures) {
            final String reason = f.reason;
            final List<Object> path = f.path;
            final Map<String, Object> data = f.data;
            final var newPath = new ArrayList<>(path);

            newPath.set(0, (Integer) newPath.get(0) - offset);

            final Map<String, Object> finalData;
            if (reason.equals("PathCollision")) {
                final var otherNewPath = new ArrayList<>((List<Object>) data.get("other"));

                otherNewPath.set(0, (Integer) otherNewPath.get(0) - offset);
                finalData = Map.of("other", otherNewPath);
            } else {
                finalData = data;
            }

            finalList.add(new SchemaParseFailure(newPath, reason, finalData));
        }

        return finalList;
    }

    private static String findSchemaKey(Map<String, Object> definition, int index) {
        final var regex = "^((fn|error|info)|((struct|union|_ext)(<[0-2]>)?))\\..*";
        final var matches = new ArrayList<String>();

        for (final var e : definition.keySet()) {
            if (e.matches(regex)) {
                matches.add(e);
            }
        }

        if (matches.size() == 1) {
            return matches.get(0);
        } else {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(List.of(index),
                    "ObjectKeyRegexMatchCountUnexpected",
                    new TreeMap<>(
                            Map.of("regex", regex, "actual", matches.size(), "expected", 1)))));
        }
    }

    private static String findMatchingSchemaKey(Set<String> schemaKeys, String schemaKey) {
        for (final var k : schemaKeys) {
            var splitK = k.split("\\.")[1];
            var splitSchemaKey = schemaKey.split("\\.")[1];
            if (Objects.equals(splitK, splitSchemaKey)) {
                return k;
            }
        }
        return null;
    }

    static List<SchemaParseFailure> getTypeUnexpectedValidationFailure(List<Object> path, Object value,
            String expectedType) {
        final var actualType = _ValidateUtil.getType(value);
        final Map<String, Object> data = new TreeMap<>(Map.ofEntries(Map.entry("actual", Map.of(actualType, Map.of())),
                Map.entry("expected", Map.of(expectedType, Map.of()))));
        return List.of(
                new SchemaParseFailure(path, "TypeUnexpected", data));
    }

}
