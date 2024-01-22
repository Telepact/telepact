package io.github.brenbar.uapi;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

class _ParseSchemaUtil {

    static UApiSchema newUApiSchema(String uApiSchemaJson, Map<String, _UType> typeExtensions) {
        final var objectMapper = new ObjectMapper();

        final Object uApiSchemaPseudoJsonInit;
        try {
            uApiSchemaPseudoJsonInit = objectMapper.readValue(uApiSchemaJson, new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new UApiSchemaParseError(
                    List.of(new _SchemaParseFailure(List.of(), "JsonInvalid", Map.of())),
                    e);
        }

        final List<Object> uApiSchemaPseudoJson;
        try {
            uApiSchemaPseudoJson = _CastUtil.asList(uApiSchemaPseudoJsonInit);
        } catch (ClassCastException e) {
            final List<_SchemaParseFailure> thisParseFailures = _ParseSchemaToolUtil
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
                    List.of(new _SchemaParseFailure(List.of(), "JsonInvalid", Map.of())),
                    e);
        }

        final List<Object> secondUApiSchemaPseudoJson;
        try {
            secondUApiSchemaPseudoJson = _CastUtil.asList(secondUApiSchemaPseudoJsonInit);
        } catch (ClassCastException e) {
            final List<_SchemaParseFailure> thisParseFailure = _ParseSchemaToolUtil
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
        final var parseFailures = new ArrayList<_SchemaParseFailure>();
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
                final List<_SchemaParseFailure> thisParseFailures = _ParseSchemaToolUtil
                        .getTypeUnexpectedValidationFailure(loopPath, definition, "Object");

                parseFailures.addAll(thisParseFailures);
                continue;
            }

            final String schemaKey;
            try {
                schemaKey = _ParseSchemaToolUtil.findSchemaKey(def, index);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
                continue;
            }

            System.out.println(schemaKeysToIndex);
            System.out.println(schemaKeys);
            System.out.println(schemaKey);
            final var matchingSchemaKey = _ParseSchemaToolUtil.findMatchingSchemaKey(schemaKeys, schemaKey);
            if (matchingSchemaKey != null) {
                final var otherPathIndex = schemaKeysToIndex.get(matchingSchemaKey);
                final List<Object> finalPath = _Util.append(loopPath, schemaKey);
                System.out.print(otherPathIndex);

                parseFailures.add(new _SchemaParseFailure(finalPath, "PathCollision",
                        Map.of("other", List.of(otherPathIndex, matchingSchemaKey))));
                continue;
            }

            schemaKeys.add(schemaKey);
            schemaKeysToIndex.put(schemaKey, index);
        }

        if (!parseFailures.isEmpty()) {
            final var offsetParseFailures = _ParseSchemaToolUtil.offsetSchemaIndex(parseFailures, pathOffset);
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
            final var offsetParseFailures = _ParseSchemaToolUtil.offsetSchemaIndex(parseFailures, pathOffset);
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
            final var offsetParseFailures = _ParseSchemaToolUtil.offsetSchemaIndex(parseFailures, pathOffset);
            throw new UApiSchemaParseError(offsetParseFailures);
        }

        return new UApiSchema(uApiSchemaPseudoJson, parsedTypes, typeExtensions);
    }
}
