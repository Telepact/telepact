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

import java.io.IOException;
import java.util.*;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

public class ParseUApiSchema {

    public static UApiSchema parseUApiSchema(Map<String, String> uApiSchemaNameToJson) {
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

        final var orderedDocuments = new TreeSet<>(uApiSchemaNameToJson.keySet());

        final var objectMapper = new ObjectMapper();
        final var uApiSchemaNameToPseudoJson = new HashMap<String, List<Object>>();

        for (var uApiSchemaJson : uApiSchemaNameToJson.entrySet()) {
            var documentName = uApiSchemaJson.getKey();

            final Object uApiSchemaPseudoJsonInit;
            try {
                uApiSchemaPseudoJsonInit = objectMapper.readValue(uApiSchemaJson.getValue(),
                        new TypeReference<>() {
                        });
            } catch (IOException e) {
                throw new UApiSchemaParseError(
                        List.of(new SchemaParseFailure(documentName, List.of(), "JsonInvalid", Map.of())),
                        uApiSchemaNameToJson,
                        e);
            }

            if (!(uApiSchemaPseudoJsonInit instanceof List)) {
                final List<SchemaParseFailure> thisParseFailure = getTypeUnexpectedParseFailure(documentName, List.of(),
                        uApiSchemaPseudoJsonInit, "Array");
                throw new UApiSchemaParseError(thisParseFailure, uApiSchemaNameToJson);
            }
            final List<Object> uApiSchemaPseudoJson = (List<Object>) uApiSchemaPseudoJsonInit;

            uApiSchemaNameToPseudoJson.put(documentName, uApiSchemaPseudoJson);
        }

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
                    var schemaKey = findSchemaKey(documentName, def, index, uApiSchemaNameToJson);
                    var matchingSchemaKey = findMatchingSchemaKey(schemaKeys, schemaKey);
                    if (matchingSchemaKey != null) {
                        var otherPathIndex = schemaKeysToIndex.get(matchingSchemaKey);
                        var otherDocumentName = schemaKeysToDocumentName.get(matchingSchemaKey);
                        var finalPath = new ArrayList<>(loopPath);
                        finalPath.add(schemaKey);
                        List<Object> finalOtherPath = new ArrayList<>(List.of(otherPathIndex, matchingSchemaKey));
                        var finalOtherDocumentJson = uApiSchemaNameToJson.get(otherDocumentName);
                        var finalOtherLocationPseudoJson = GetPathDocumentCoordinatesPseudoJson
                                .getPathDocumentCoordinatesPseudoJson(finalOtherPath, finalOtherDocumentJson);

                        parseFailures.add(new SchemaParseFailure(
                                documentName,
                                finalPath,
                                "PathCollision",
                                Map.of("document", otherDocumentName, "path", finalOtherPath,
                                        "location", finalOtherLocationPseudoJson)));
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
            throw new UApiSchemaParseError(parseFailures, uApiSchemaNameToJson);
        }

        var requestHeaderKeys = new HashSet<String>();
        var responseHeaderKeys = new HashSet<String>();
        var errorKeys = new HashSet<String>();

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
                        schemaKey,
                        new ParseContext(
                                thisDocumentName,
                                List.of(thisIndex),
                                uApiSchemaNameToPseudoJson,
                                uApiSchemaNameToJson,
                                schemaKeysToDocumentName,
                                schemaKeysToIndex,
                                parsedTypes,
                                parseFailures,
                                failedTypes));
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures, uApiSchemaNameToJson);
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
                        thisKey,
                        new ParseContext(
                                thisDocumentName,
                                List.of(thisIndex),
                                uApiSchemaNameToPseudoJson,
                                uApiSchemaNameToJson,
                                schemaKeysToDocumentName,
                                schemaKeysToIndex,
                                parsedTypes,
                                parseFailures,
                                failedTypes));
                errors.add(error);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures, uApiSchemaNameToJson);
        }

        try {
            catchErrorCollisions(uApiSchemaNameToPseudoJson, errorKeys, schemaKeysToIndex, schemaKeysToDocumentName,
                    uApiSchemaNameToJson);
        } catch (UApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures, uApiSchemaNameToJson);
        }

        for (var error : errors) {
            try {
                applyErrorToParsedTypes(error, parsedTypes, schemaKeysToDocumentName, schemaKeysToIndex,
                        uApiSchemaNameToJson);
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
                        def,
                        requestHeaderKey,
                        headerField,
                        new ParseContext(
                                thisDocumentName,
                                List.of(thisIndex, requestHeaderKey),
                                uApiSchemaNameToPseudoJson,
                                uApiSchemaNameToJson,
                                schemaKeysToDocumentName,
                                schemaKeysToIndex,
                                parsedTypes,
                                parseFailures,
                                failedTypes));
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
                        def,
                        responseHeaderKey,
                        headerField,
                        new ParseContext(
                                thisDocumentName,
                                List.of(thisIndex, responseHeaderKey),
                                uApiSchemaNameToPseudoJson,
                                uApiSchemaNameToJson,
                                schemaKeysToDocumentName,
                                schemaKeysToIndex,
                                parsedTypes,
                                parseFailures,
                                failedTypes));
                responseHeaders.put(responseHeaderType.fieldName, responseHeaderType);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures, uApiSchemaNameToJson);
        }

        final var finalOriginalSchema = new ArrayList<>(originalSchema.values());

        return new UApiSchema(
                finalOriginalSchema,
                parsedTypes,
                requestHeaders,
                responseHeaders);
    }
}
