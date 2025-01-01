package uapi.internal.schema;

import static uapi.internal.schema.ApplyErrorToParsedTypes.applyErrorToParsedTypes;
import static uapi.internal.schema.CatchErrorCollisions.catchErrorCollisions;
import static uapi.internal.schema.FindMatchingSchemaKey.findMatchingSchemaKey;
import static uapi.internal.schema.FindSchemaKey.findSchemaKey;
import static uapi.internal.schema.GetOrParseType.getOrParseType;
import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static uapi.internal.schema.ParseErrorType.parseErrorType;
import static uapi.internal.schema.ParseHeadersType.parseHeadersType;

import uapi.UApiSchema;
import uapi.UApiSchemaParseError;
import uapi.internal.types.UError;
import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UType;
import java.util.*;

public class ParseUApiSchema {

    public static UApiSchema parseUApiSchema(Map<String, List<Object>> uApiSchemaNameToPseudoJson) {
        final var originalSchema = new TreeMap<String, Object>((k1, k2) -> {
            if (k1.equals(k2)) {
                return 0;
            } else if (k1.startsWith("info.")) {
                return -1;
            } else if (k2.startsWith("info.")) {
                return 1;
            } else {
                return k1.compareTo(k2);
            }
        });
        final var parsedTypes = new HashMap<String, UType>();
        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var failedTypes = new HashSet<String>();
        final var schemaKeysToIndex = new HashMap<String, Integer>();
        final var schemaKeysToDocumentName = new HashMap<String, String>();
        final var schemaKeys = new HashSet<String>();

        final var orderedDocuments = new TreeSet<>(uApiSchemaNameToPseudoJson.keySet());

        for (var documentName : orderedDocuments) {
            var uApiSchemaPseudoJson = uApiSchemaNameToPseudoJson.get(documentName);

            int index = -1;
            for (Object definition : uApiSchemaPseudoJson) {
                index++;
                var loopPath = new ArrayList<Object>(List.of(index));

                if (!(definition instanceof Map)) {
                    var thisParseFailures = getTypeUnexpectedParseFailure(
                            documentName, (List<Object>) loopPath, definition, "Object");
                    parseFailures.addAll(thisParseFailures);
                    continue;
                }

                var def = (Map<String, Object>) definition;

                try {
                    var schemaKey = findSchemaKey(documentName, def, index);
                    var matchingSchemaKey = findMatchingSchemaKey(schemaKeys, schemaKey);
                    if (matchingSchemaKey != null) {
                        var otherPathIndex = schemaKeysToIndex.get(matchingSchemaKey);
                        var otherDocumentName = schemaKeysToDocumentName.get(matchingSchemaKey);
                        var finalPath = new ArrayList<>(loopPath);
                        finalPath.add(schemaKey);
                        parseFailures.add(new SchemaParseFailure(
                                documentName,
                                finalPath,
                                "PathCollision",
                                Map.of("document", otherDocumentName, "path",
                                        List.of(otherPathIndex, matchingSchemaKey))));
                        continue;
                    }

                    schemaKeys.add(schemaKey);
                    schemaKeysToIndex.put(schemaKey, index);
                    schemaKeysToDocumentName.put(schemaKey, documentName);
                    if (!documentName.endsWith("_")) {
                        originalSchema.put(schemaKey, def);
                    }
                } catch (UApiSchemaParseError e) {
                    parseFailures.addAll(e.schemaParseFailures);
                }
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
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
            var thisDocumentName = schemaKeysToDocumentName.get(schemaKey);

            try {
                getOrParseType(
                        thisDocumentName,
                        Collections.singletonList(thisIndex),
                        schemaKey,
                        rootTypeParameterCount,
                        uApiSchemaNameToPseudoJson,
                        schemaKeysToDocumentName,
                        schemaKeysToIndex,
                        parsedTypes,
                        parseFailures,
                        failedTypes);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        var errors = new ArrayList<UError>();

        for (String thisKey : errorKeys) {
            var thisIndex = schemaKeysToIndex.get(thisKey);
            var thisDocumentName = schemaKeysToDocumentName.get(thisKey);
            var uApiSchemaPseudoJson = uApiSchemaNameToPseudoJson.get(thisDocumentName);
            var def = (Map<String, Object>) uApiSchemaPseudoJson.get(thisIndex);

            try {
                var error = parseErrorType(
                        def,
                        thisDocumentName,
                        uApiSchemaNameToPseudoJson,
                        thisKey,
                        thisIndex,
                        schemaKeysToDocumentName,
                        schemaKeysToIndex,
                        parsedTypes,
                        parseFailures,
                        failedTypes);
                errors.add(error);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        try {
            catchErrorCollisions(uApiSchemaNameToPseudoJson, errorKeys, schemaKeysToIndex, schemaKeysToDocumentName);
        } catch (UApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        for (var error : errors) {
            try {
                applyErrorToParsedTypes(error, parsedTypes, schemaKeysToDocumentName, schemaKeysToIndex);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        var requestHeaders = new HashMap<String, UFieldDeclaration>();
        var responseHeaders = new HashMap<String, UFieldDeclaration>();

        for (String requestHeaderKey : requestHeaderKeys) {
            var thisIndex = schemaKeysToIndex.get(requestHeaderKey);
            var thisDocumentName = schemaKeysToDocumentName.get(requestHeaderKey);
            var uApiSchemaPseudoJson = uApiSchemaNameToPseudoJson.get(thisDocumentName);
            var def = (Map<String, Object>) uApiSchemaPseudoJson.get(thisIndex);
            var headerField = requestHeaderKey.substring("requestHeader.".length());

            try {
                var requestHeaderType = parseHeadersType(
                        thisDocumentName,
                        def,
                        requestHeaderKey,
                        headerField,
                        thisIndex,
                        uApiSchemaNameToPseudoJson,
                        schemaKeysToDocumentName,
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
            var thisDocumentName = schemaKeysToDocumentName.get(responseHeaderKey);
            var uApiSchemaPseudoJson = uApiSchemaNameToPseudoJson.get(thisDocumentName);
            var def = (Map<String, Object>) uApiSchemaPseudoJson.get(thisIndex);
            var headerField = responseHeaderKey.substring("responseHeader.".length());

            try {
                var responseHeaderType = parseHeadersType(
                        thisDocumentName,
                        def,
                        responseHeaderKey,
                        headerField,
                        thisIndex,
                        uApiSchemaNameToPseudoJson,
                        schemaKeysToDocumentName,
                        schemaKeysToIndex,
                        parsedTypes,
                        parseFailures,
                        failedTypes);
                responseHeaders.put(responseHeaderType.fieldName, responseHeaderType);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        final var finalOriginalSchema = new ArrayList<>(originalSchema.values());

        return new UApiSchema(
                finalOriginalSchema,
                parsedTypes,
                requestHeaders,
                responseHeaders);
    }
}
