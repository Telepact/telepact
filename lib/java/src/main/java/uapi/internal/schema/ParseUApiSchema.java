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
import java.util.*;

public class ParseUApiSchema {

    public static UApiSchema parseUApiSchema(List<Object> uApiSchemaPseudoJson, int pathOffset) {
        final var parsedTypes = new HashMap<String, UType>();
        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var failedTypes = new HashSet<String>();
        final var schemaKeysToIndex = new HashMap<String, Integer>();
        final var schemaKeys = new HashSet<String>();

        int index = -1;
        for (Object definition : uApiSchemaPseudoJson) {
            index++;
            var loopPath = new ArrayList<Object>(Collections.singletonList(index));

            if (!(definition instanceof Map)) {
                var thisParseFailures = getTypeUnexpectedParseFailure(
                        (List<Object>) loopPath, definition, "Object");
                parseFailures.addAll(thisParseFailures);
                continue;
            }

            var def = (Map<String, Object>) definition;

            try {
                var schemaKey = findSchemaKey(def, index);
                var ignoreIfDuplicate = (boolean) def.getOrDefault("_ignoreIfDuplicate", false);
                var matchingSchemaKey = findMatchingSchemaKey(schemaKeys, schemaKey);
                if (matchingSchemaKey != null) {
                    if (!ignoreIfDuplicate) {
                        var otherPathIndex = schemaKeysToIndex.get(matchingSchemaKey);
                        var finalPath = new ArrayList<>(loopPath);
                        finalPath.add(schemaKey);
                        parseFailures.add(new SchemaParseFailure(
                                finalPath,
                                "PathCollision",
                                Map.of("other", List.of(otherPathIndex, matchingSchemaKey)),
                                schemaKey));
                    }
                    continue;
                }

                schemaKeys.add(schemaKey);
                schemaKeysToIndex.put(schemaKey, index);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            var offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset, schemaKeysToIndex);
            throw new UApiSchemaParseError(offsetParseFailures);
        }

        var requestHeaderKeys = new HashSet<String>();
        var responseHeaderKeys = new HashSet<String>();
        var errorKeys = new HashSet<String>();
        var rootTypeParameterCount = 0;

        for (String schemaKey : schemaKeys) {
            if (schemaKey.startsWith("info.")) {
                continue;
            } else if (schemaKey.startsWith("requestHeader.")) {
                requestHeaderKeys.add(schemaKey);
                continue;
            } else if (schemaKey.startsWith("responseHeader.")) {
                responseHeaderKeys.add(schemaKey);
                continue;
            } else if (schemaKey.startsWith("errors.")) {
                errorKeys.add(schemaKey);
                continue;
            }

            var thisIndex = schemaKeysToIndex.get(schemaKey);

            try {
                getOrParseType(
                        Collections.singletonList(thisIndex),
                        schemaKey,
                        rootTypeParameterCount,
                        uApiSchemaPseudoJson,
                        schemaKeysToIndex,
                        parsedTypes,
                        parseFailures,
                        failedTypes);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            var offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset, schemaKeysToIndex);
            throw new UApiSchemaParseError(offsetParseFailures);
        }

        try {
            catchErrorCollisions(uApiSchemaPseudoJson, errorKeys, schemaKeysToIndex);

            for (String thisKey : errorKeys) {
                var thisIndex = schemaKeysToIndex.get(thisKey);
                var def = (Map<String, Object>) uApiSchemaPseudoJson.get(thisIndex);

                try {
                    var error = parseErrorType(
                            def,
                            uApiSchemaPseudoJson,
                            thisKey,
                            thisIndex,
                            schemaKeysToIndex,
                            parsedTypes,
                            parseFailures,
                            failedTypes);
                    applyErrorToParsedTypes(
                            thisKey, thisIndex, error, parsedTypes, schemaKeysToIndex);
                } catch (UApiSchemaParseError e) {
                    parseFailures.addAll(e.schemaParseFailures);
                }
            }
        } catch (UApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        var requestHeaders = new HashMap<String, UFieldDeclaration>();
        var responseHeaders = new HashMap<String, UFieldDeclaration>();

        try {
            for (String requestHeaderKey : requestHeaderKeys) {
                var thisIndex = schemaKeysToIndex.get(requestHeaderKey);
                var def = (Map<String, Object>) uApiSchemaPseudoJson.get(thisIndex);
                var headerField = requestHeaderKey.substring("requestHeader.".length());

                try {
                    var requestHeaderType = parseHeadersType(
                            def,
                            requestHeaderKey,
                            headerField,
                            thisIndex,
                            uApiSchemaPseudoJson,
                            schemaKeysToIndex,
                            parsedTypes,
                            parseFailures,
                            failedTypes);
                    requestHeaders.put(requestHeaderType.fieldName, requestHeaderType);
                } catch (UApiSchemaParseError e) {
                    parseFailures.addAll(e.schemaParseFailures);
                }
            }

            for (String responseHeaderKey : responseHeaderKeys) {
                var thisIndex = schemaKeysToIndex.get(responseHeaderKey);
                var def = (Map<String, Object>) uApiSchemaPseudoJson.get(thisIndex);
                var headerField = responseHeaderKey.substring("responseHeader.".length());

                try {
                    var responseHeaderType = parseHeadersType(
                            def,
                            responseHeaderKey,
                            headerField,
                            thisIndex,
                            uApiSchemaPseudoJson,
                            schemaKeysToIndex,
                            parsedTypes,
                            parseFailures,
                            failedTypes);
                    responseHeaders.put(responseHeaderType.fieldName, responseHeaderType);
                } catch (UApiSchemaParseError e) {
                    parseFailures.addAll(e.schemaParseFailures);
                }
            }
        } catch (UApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        if (!parseFailures.isEmpty()) {
            var offsetParseFailures = offsetSchemaIndex(parseFailures, pathOffset, schemaKeysToIndex);
            throw new UApiSchemaParseError(offsetParseFailures);
        }

        return new UApiSchema(
                uApiSchemaPseudoJson,
                parsedTypes,
                requestHeaders,
                responseHeaders);
    }
}
