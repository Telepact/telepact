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
import java.util.TreeSet;

class _ParseSchemaUtil {

    static JApiSchema extendUApiSchema(JApiSchema first, String secondUApiSchemaJson,
            Map<String, TypeExtension> secondTypeExtensions) {
        var objectMapper = new ObjectMapper();
        List<Object> secondOriginal;
        try {
            secondOriginal = objectMapper.readValue(secondUApiSchemaJson, new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new JApiSchemaParseError(
                    List.of(new SchemaParseFailure(List.of(), "ArrayTypeRequired", Map.of())),
                    e);
        }

        List<Object> firstOriginal = first.original;
        Map<String, TypeExtension> firstTypeExtensions = first.typeExtensions;

        var original = new ArrayList<Object>();
        original.addAll(firstOriginal);
        original.addAll(secondOriginal);

        var typeExtensions = new HashMap<String, TypeExtension>();
        typeExtensions.putAll(firstTypeExtensions);
        typeExtensions.putAll(secondTypeExtensions);

        return parseUApiSchema(original, typeExtensions, firstOriginal.size());
    }

    static JApiSchema newUApiSchema(String uApiSchemaJson, Map<String, TypeExtension> typeExtensions) {
        var objectMapper = new ObjectMapper();
        List<Object> internalJApiSchemaOriginal;
        try {
            internalJApiSchemaOriginal = objectMapper.readValue(_InternalJApiUtil.getJson(), new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new JApiSchemaParseError(
                    List.of(new SchemaParseFailure(List.of(), "ArrayTypeRequired", Map.of())),
                    e);
        }

        var internalApi = parseUApiSchema(internalJApiSchemaOriginal, Map.of(), 0);

        return extendUApiSchema(internalApi, uApiSchemaJson, typeExtensions);
    }

    private static JApiSchema parseUApiSchema(List<Object> originalUApiSchema,
            Map<String, TypeExtension> typeExtensions, int offset) {
        var parsedTypes = new HashMap<String, UType>();
        var parseFailures = new ArrayList<SchemaParseFailure>();
        var failedTypes = new HashSet<String>();

        var schemaKeysToIndex = new HashMap<String, Integer>();

        var schemaKeys = new HashSet<String>();
        var index = -1;
        for (var definition : originalUApiSchema) {
            index += 1;
            Map<String, Object> def;
            try {
                def = (Map<String, Object>) definition;
            } catch (ClassCastException e) {
                parseFailures
                        .add(new SchemaParseFailure(List.of(index), "DefinitionMustBeAnObject", Map.of()));
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
                parseFailures.add(new SchemaParseFailure(List.of(index), "DuplicateSchemaKey",
                        Map.of("schemaKey", schemaKey)));
            }
            schemaKeys.add(schemaKey);
            schemaKeysToIndex.put(schemaKey, index);
        }

        if (!parseFailures.isEmpty()) {
            var offsetParseFailures = offsetSchemaIndex(parseFailures, offset);
            throw new JApiSchemaParseError(offsetParseFailures);
        }

        var traitKeys = new HashSet<String>();
        var traits = new ArrayList<UTrait>();

        var rootTypeParameterCount = 0;
        boolean allowTraitsAndInfo = true;
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
                var typ = _ParseSchemaTypeUtil.getOrParseType(List.of(thisIndex), schemaKey, rootTypeParameterCount,
                        allowTraitsAndInfo,
                        originalUApiSchema,
                        schemaKeysToIndex,
                        parsedTypes, typeExtensions, parseFailures, failedTypes);
                if (typ instanceof UTrait t) {
                    traits.add(t);
                }
            } catch (JApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            var offsetParseFailures = offsetSchemaIndex(parseFailures, offset);
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

        // Ensure all type extensions are defined
        for (var entry : typeExtensions.entrySet()) {
            var typeExtensionName = entry.getKey();
            var typeExtension = (UExt) parsedTypes.get(typeExtensionName);
            if (typeExtension == null) {
                parseFailures
                        .add(new SchemaParseFailure(List.of(), "UndefinedTypeExtension",
                                Map.of("name", typeExtensionName)));
            }
        }

        if (!parseFailures.isEmpty()) {
            var offsetParseFailures = offsetSchemaIndex(parseFailures, offset);
            throw new JApiSchemaParseError(offsetParseFailures);
        }

        return new JApiSchema(originalUApiSchema, parsedTypes, typeExtensions);
    }

    private static List<SchemaParseFailure> offsetSchemaIndex(List<SchemaParseFailure> initialFailures, int offset) {
        return initialFailures.stream().map(f -> {
            List<Object> newPath;
            if (f.path.size() == 0) {
                newPath = f.path;
            } else {
                newPath = new ArrayList<>(f.path);
                newPath.set(0, (Integer) newPath.get(0) - offset);
            }
            return new SchemaParseFailure(newPath, f.reason, f.data);
        })
                .toList();
    }

    private static String findSchemaKey(Map<String, Object> definition, int index) {
        var regex = "^((fn|trait|info)|((struct|union|ext)(<[0-2]>)?))\\..*";
        var matches = new ArrayList<String>();
        for (var e : definition.keySet()) {
            if (e.matches(regex)) {
                matches.add(e);
            }
        }
        if (matches.size() == 1) {
            return matches.get(0);
        } else {
            Map<String, Object> sortedMap = new TreeMap<>(Map.of("regex", regex));
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(List.of(index),
                    "DefinitionMustHaveOneKeyMatchingRegex", sortedMap)));
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
