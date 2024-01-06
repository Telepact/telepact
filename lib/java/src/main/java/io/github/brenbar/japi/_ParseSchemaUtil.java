package io.github.brenbar.japi;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.TreeSet;

class _ParseSchemaUtil {

    static JApiSchema combineUApiSchemas(JApiSchema first, JApiSchema second) {
        List<Object> firstOriginal = first.original;
        List<Object> secondOriginal = second.original;
        Map<String, UType> firstParsed = first.parsed;
        Map<String, UType> secondParsed = second.parsed;
        Map<String, TypeExtension> firstTypeExtensions = first.typeExtensions;
        Map<String, TypeExtension> secondTypeExtensions = second.typeExtensions;

        var original = new ArrayList<Object>();
        original.addAll(firstOriginal);
        original.addAll(secondOriginal);

        var typeExtensions = new HashMap<String, TypeExtension>();
        typeExtensions.putAll(firstTypeExtensions);
        typeExtensions.putAll(secondTypeExtensions);

        return parseUApiSchema(original, typeExtensions);
    }

    static JApiSchema parseUApiSchema(String uApiSchemaJson, Map<String, TypeExtension> typeExtensions) {
        var objectMapper = new ObjectMapper();
        List<Object> originalUApiSchema;
        try {
            originalUApiSchema = objectMapper.readValue(uApiSchemaJson, new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new JApiSchemaParseError(
                    List.of(new SchemaParseFailure(List.of(), "ArrayTypeRequired", Map.of())),
                    e);
        }

        return parseUApiSchema(originalUApiSchema, typeExtensions);
    }

    private static JApiSchema parseUApiSchema(List<Object> originalUApiSchema,
            Map<String, TypeExtension> typeExtensions) {
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
            throw new JApiSchemaParseError(parseFailures);
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
            var typ = _ParseSchemaTypeUtil.getOrParseType(List.of(thisIndex), schemaKey, rootTypeParameterCount,
                    allowTraitsAndInfo,
                    originalUApiSchema,
                    schemaKeysToIndex,
                    parsedTypes, typeExtensions, parseFailures, failedTypes);
            if (typ instanceof UTrait t) {
                traits.add(t);
            }
        }

        for (var traitKey : traitKeys) {
            var thisIndex = schemaKeysToIndex.get(traitKey);
            var def = (Map<String, Object>) originalUApiSchema.get(thisIndex);

            try {
                var trait = _ParseSchemaTraitTypeUtil.parseTraitType(def, traitKey, originalUApiSchema,
                        schemaKeysToIndex,
                        parsedTypes,
                        typeExtensions, parseFailures, failedTypes);
                _ParseSchemaTraitTypeUtil.applyTraitToParsedTypes(trait, parsedTypes, schemaKeysToIndex);
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
            throw new JApiSchemaParseError(parseFailures);
        }

        return new JApiSchema(originalUApiSchema, parsedTypes, typeExtensions);
    }

    private static String findSchemaKey(Map<String, Object> definition, int index) {
        var regex = "^((fn|trait|info)|((struct|union|ext)(<[0-2]>)?))\\..*";
        for (var e : definition.keySet()) {
            if (e.matches(regex)) {
                return e;
            }
        }
        Map<String, Object> sortedMap = new TreeMap<>(Map.of("regex", regex));
        throw new JApiSchemaParseError(List.of(new SchemaParseFailure(List.of(index),
                "DefinitionMustHaveOneKeyMatchingRegex", sortedMap)));
    }

}
