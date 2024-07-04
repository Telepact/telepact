package uapi.internal.schema;

import static uapi.internal.schema.ApplyErrorToParsedTypes.applyErrorToParsedTypes;
import static uapi.internal.schema.CatchErrorCollisions.catchErrorCollisions;
import static uapi.internal.schema.FindMatchingSchemaKey.findMatchingSchemaKey;
import static uapi.internal.schema.FindSchemaKey.findSchemaKey;
import static uapi.internal.schema.GetOrParseType.getOrParseType;
import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static uapi.internal.schema.OffsetSchemaIndex.offsetSchemaIndex;
import static uapi.internal.schema.ParseErrorType.parseErrorType;
import static uapi.internal.schema.ParseHeadersType.parseHeadersType;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

import uapi.UApiSchema;
import uapi.UApiSchemaParseError;
import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UType;

public class ParseUApiSchema {
    public static UApiSchema parseUApiSchema(List<Object> uApiSchemaPseudoJson,
            int pathOffset) {
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

            if (!(definition instanceof Map)) {
                final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(loopPath,
                        definition, "Object");

                parseFailures.addAll(thisParseFailures);
                continue;
            }
            final Map<String, Object> def = (Map<String, Object>) definition;

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

                    final List<Object> finalPath = new ArrayList<>(loopPath);
                    finalPath.add(schemaKey);

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
                        uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, parseFailures,
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
                            schemaKeysToIndex, parsedTypes, parseFailures, failedTypes);
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
                            schemaKeysToIndex, parsedTypes, parseFailures, failedTypes);
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
                            schemaKeysToIndex, parsedTypes, parseFailures, failedTypes);
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

        return new UApiSchema(uApiSchemaPseudoJson, parsedTypes, requestHeaders, responseHeaders);
    }
}
