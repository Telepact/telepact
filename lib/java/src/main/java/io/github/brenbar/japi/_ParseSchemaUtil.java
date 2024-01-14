package io.github.brenbar.japi;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

class _ParseSchemaUtil {

    static JApiSchema extendUApiSchema(JApiSchema first, String secondUApiSchemaJson,
            Map<String, _UType> secondTypeExtensions) {
        var objectMapper = new ObjectMapper();
        Object secondOriginalInit;
        try {
            secondOriginalInit = objectMapper.readValue(secondUApiSchemaJson, new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new JApiSchemaParseError(
                    List.of(new SchemaParseFailure(List.of(), "JsonInvalid", Map.of())),
                    e);
        }

        List<Object> secondOriginal;
        try {
            secondOriginal = _CastUtil.asList(secondOriginalInit);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(
                    _ParseSchemaUtil.getTypeUnexpectedValidationFailure(List.of(), secondOriginalInit, "Array"),
                    e);
        }

        List<Object> firstOriginal = first.original;
        Map<String, _UType> firstTypeExtensions = first.typeExtensions;

        var original = new ArrayList<Object>();
        original.addAll(firstOriginal);
        original.addAll(secondOriginal);

        var typeExtensions = new HashMap<String, _UType>();
        typeExtensions.putAll(firstTypeExtensions);
        typeExtensions.putAll(secondTypeExtensions);

        return parseUApiSchema(original, typeExtensions, firstOriginal.size());
    }

    static JApiSchema newUApiSchema(String uApiSchemaJson, Map<String, _UType> typeExtensions) {
        var objectMapper = new ObjectMapper();
        Object originalInit;
        try {
            originalInit = objectMapper.readValue(uApiSchemaJson, new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new JApiSchemaParseError(
                    List.of(new SchemaParseFailure(List.of(), "JsonInvalid", Map.of())),
                    e);
        }

        List<Object> original;
        try {
            original = _CastUtil.asList(originalInit);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(
                    _ParseSchemaUtil.getTypeUnexpectedValidationFailure(List.of(), originalInit, "Array"),
                    e);
        }

        return parseUApiSchema(original, typeExtensions, 0);
    }

    private static JApiSchema parseUApiSchema(List<Object> originalUApiSchema,
            Map<String, _UType> typeExtensions, int pathOffset) {
        var parsedTypes = new HashMap<String, _UType>();
        var parseFailures = new ArrayList<SchemaParseFailure>();
        var failedTypes = new HashSet<String>();

        var schemaKeysToIndex = new HashMap<String, Integer>();

        var schemaKeys = new HashSet<String>();
        var index = -1;
        for (var definition : originalUApiSchema) {
            index += 1;

            List<Object> loopPath = List.of(index);

            Map<String, Object> def;
            try {
                def = _CastUtil.asMap(definition);
            } catch (ClassCastException e) {
                parseFailures
                        .addAll(_ParseSchemaUtil.getTypeUnexpectedValidationFailure(loopPath, definition, "Object"));
                continue;
            }

            String schemaKey;
            try {
                schemaKey = findSchemaKey(def, index);
            } catch (JApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
                continue;
            }

            if (schemaKeys.contains(schemaKey)) {
                var otherPathIndex = schemaKeysToIndex.get(schemaKey);
                parseFailures.add(new SchemaParseFailure(_ValidateUtil.append(loopPath, schemaKey), "PathCollision",
                        Map.of("other", List.of(otherPathIndex, schemaKey))));
            }
            schemaKeys.add(schemaKey);
            schemaKeysToIndex.put(schemaKey, index);
        }

        if (!parseFailures.isEmpty()) {
            var offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset);
            throw new JApiSchemaParseError(offsetParseFailures);
        }

        var traitKeys = new HashSet<String>();

        var rootTypeParameterCount = 0;
        for (var schemaKey : schemaKeys) {
            if (schemaKey.startsWith("info.")) {
                continue;
            }
            if (schemaKey.startsWith("trait.")) {
                traitKeys.add(schemaKey);
                continue;
            }
            var thisIndex = schemaKeysToIndex.get(schemaKey);
            try {
                _ParseSchemaTypeUtil.getOrParseType(List.of(thisIndex), schemaKey, rootTypeParameterCount,
                        originalUApiSchema,
                        schemaKeysToIndex,
                        parsedTypes, typeExtensions, parseFailures, failedTypes);
            } catch (JApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            var offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset);
            throw new JApiSchemaParseError(offsetParseFailures);
        }

        for (var traitKey : traitKeys) {
            var thisIndex = schemaKeysToIndex.get(traitKey);
            var def = (Map<String, Object>) originalUApiSchema.get(thisIndex);

            try {
                var trait = _ParseSchemaTraitUtil.parseTraitType(def, traitKey, originalUApiSchema,
                        schemaKeysToIndex,
                        parsedTypes,
                        typeExtensions, parseFailures, failedTypes);
                _ParseSchemaTraitUtil.applyTraitToParsedTypes(trait, parsedTypes, schemaKeysToIndex);
            } catch (JApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            var offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset);
            throw new JApiSchemaParseError(offsetParseFailures);
        }

        return new JApiSchema(originalUApiSchema, parsedTypes, typeExtensions);
    }

    private static List<SchemaParseFailure> offsetSchemaIndex(List<SchemaParseFailure> initialFailures, int offset) {
        return initialFailures.stream().map(f -> {
            List<Object> newPath = new ArrayList<>(f.path);
            newPath.set(0, (Integer) newPath.get(0) - offset);

            Map<String, Object> finalData;
            if (f.reason.equals("PathCollision")) {
                List<Object> otherNewPath = new ArrayList<>((List<Object>) f.data.get("other"));
                otherNewPath.set(0, (Integer) otherNewPath.get(0) - offset);
                finalData = Map.of("other", otherNewPath);
            } else {
                finalData = f.data;
            }

            return new SchemaParseFailure(newPath, f.reason, finalData);
        })
                .toList();
    }

    private static String findSchemaKey(Map<String, Object> definition, int index) {
        var regex = "^((fn|trait|info)|((struct|union|_ext)(<[0-2]>)?))\\..*";
        var matches = new ArrayList<String>();
        for (var e : definition.keySet()) {
            if (e.matches(regex)) {
                matches.add(e);
            }
        }
        if (matches.size() == 1) {
            return matches.get(0);
        } else {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(List.of(index),
                    "ObjectKeyRegexMatchCountUnexpected",
                    new TreeMap<>(
                            Map.of("regex", regex, "actual", matches.size(), "expected", 1)))));
        }
    }

    static List<SchemaParseFailure> getTypeUnexpectedValidationFailure(List<Object> path, Object value,
            String expectedType) {
        var actualType = _ValidateUtil.getType(value);
        Map<String, Object> data = new TreeMap<>(Map.ofEntries(Map.entry("actual", Map.of(actualType, Map.of())),
                Map.entry("expected", Map.of(expectedType, Map.of()))));
        return Collections.singletonList(
                new SchemaParseFailure(path, "TypeUnexpected", data));
    }

}
