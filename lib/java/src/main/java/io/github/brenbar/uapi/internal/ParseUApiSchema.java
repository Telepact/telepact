package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.UApiSchema;
import io.github.brenbar.uapi.UApiSchemaParseError;
import io.github.brenbar.uapi.internal.types.UFieldDeclaration;
import io.github.brenbar.uapi.internal.types.UType;

import static io.github.brenbar.uapi.internal.AsMap.asMap;
import static io.github.brenbar.uapi.internal.ParseErrorType.parseErrorType;
import static io.github.brenbar.uapi.internal.ApplyErrorToParsedTypes.applyErrorToParsedTypes;
import static io.github.brenbar.uapi.internal.CatchErrorCollisions.catchErrorCollisions;
import static io.github.brenbar.uapi.internal.FindMatchingSchemaKey.findMatchingSchemaKey;
import static io.github.brenbar.uapi.internal.FindSchemaKey.findSchemaKey;
import static io.github.brenbar.uapi.internal.GetOrParseType.getOrParseType;
import static io.github.brenbar.uapi.internal.OffsetSchemaIndex.offsetSchemaIndex;
import static io.github.brenbar.uapi.internal.ParseHeadersType.parseHeadersType;
import static io.github.brenbar.uapi.internal.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.brenbar.uapi.internal.Append.append;

public class ParseUApiSchema {
    public static UApiSchema parseUApiSchema(List<Object> uApiSchemaPseudoJson,
            Map<String, UType> typeExtensions, int pathOffset) {
        final var parsedTypes = new HashMap<String, UType>();
        final var parseFailures = new ArrayList<SchemaParseFailure>();
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
                final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(loopPath,
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

                    parseFailures.add(new SchemaParseFailure(finalPath, "PathCollision",
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

        final Map<String, UFieldDeclaration> requestHeaders = new HashMap<>();
        final Map<String, UFieldDeclaration> responseHeaders = new HashMap<>();

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
}
