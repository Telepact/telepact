package io.github.telepact.internal.schema;

import static io.github.telepact.internal.schema.ApplyErrorToParsedTypes.applyErrorToParsedTypes;
import static io.github.telepact.internal.schema.CatchErrorCollisions.catchErrorCollisions;
import static io.github.telepact.internal.schema.CatchHeaderCollisions.catchHeaderCollisions;
import static io.github.telepact.internal.schema.FindMatchingSchemaKey.findMatchingSchemaKey;
import static io.github.telepact.internal.schema.FindSchemaKey.findSchemaKey;
import static io.github.telepact.internal.schema.GetOrParseType.getOrParseType;
import static io.github.telepact.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.telepact.internal.schema.ParseErrorType.parseErrorType;
import static io.github.telepact.internal.schema.ParseHeadersType.parseHeadersType;

import java.io.IOException;
import java.util.*;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.telepact.TelepactSchema;
import io.github.telepact.TelepactSchemaParseError;
import io.github.telepact.internal.types.VError;
import io.github.telepact.internal.types.VFieldDeclaration;
import io.github.telepact.internal.types.VHeaders;
import io.github.telepact.internal.types.VType;

public class ParseTelepactSchema {

    public static TelepactSchema parseTelepactSchema(Map<String, String> telepactSchemaNameToJson) {
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
        final var parsedTypes = new HashMap<String, VType>();
        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var failedTypes = new HashSet<String>();
        final var schemaKeysToIndex = new HashMap<String, Integer>();
        final var schemaKeysToDocumentName = new HashMap<String, String>();
        final var schemaKeys = new HashSet<String>();

        final var orderedDocuments = new TreeSet<>(telepactSchemaNameToJson.keySet());

        final var objectMapper = new ObjectMapper();
        final var telepactSchemaNameToPseudoJson = new HashMap<String, List<Object>>();

        for (var telepactSchemaJson : telepactSchemaNameToJson.entrySet()) {
            var documentName = telepactSchemaJson.getKey();

            final Object telepactSchemaPseudoJsonInit;
            try {
                telepactSchemaPseudoJsonInit = objectMapper.readValue(telepactSchemaJson.getValue(),
                        new TypeReference<>() {
                        });
            } catch (IOException e) {
                throw new TelepactSchemaParseError(
                        List.of(new SchemaParseFailure(documentName, List.of(), "JsonInvalid", Map.of())),
                        telepactSchemaNameToJson,
                        e);
            }

            if (!(telepactSchemaPseudoJsonInit instanceof List)) {
                final List<SchemaParseFailure> thisParseFailure = getTypeUnexpectedParseFailure(documentName, List.of(),
                        telepactSchemaPseudoJsonInit, "Array");
                throw new TelepactSchemaParseError(thisParseFailure, telepactSchemaNameToJson);
            }
            final List<Object> telepactSchemaPseudoJson = (List<Object>) telepactSchemaPseudoJsonInit;

            telepactSchemaNameToPseudoJson.put(documentName, telepactSchemaPseudoJson);
        }

        for (var documentName : orderedDocuments) {
            var telepactSchemaPseudoJson = telepactSchemaNameToPseudoJson.get(documentName);

            int index = -1;
            for (Object definition : telepactSchemaPseudoJson) {
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
                    var schemaKey = findSchemaKey(documentName, def, index, telepactSchemaNameToJson);
                    var matchingSchemaKey = findMatchingSchemaKey(schemaKeys, schemaKey);
                    if (matchingSchemaKey != null) {
                        var otherPathIndex = schemaKeysToIndex.get(matchingSchemaKey);
                        var otherDocumentName = schemaKeysToDocumentName.get(matchingSchemaKey);
                        var finalPath = new ArrayList<>(loopPath);
                        finalPath.add(schemaKey);
                        List<Object> finalOtherPath = new ArrayList<>(List.of(otherPathIndex, matchingSchemaKey));
                        var finalOtherDocumentJson = telepactSchemaNameToJson.get(otherDocumentName);
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
                    if ("auto_".equals(documentName) || !documentName.endsWith("_")) {
                        originalSchema.put(schemaKey, def);
                    }
                } catch (TelepactSchemaParseError e) {
                    parseFailures.addAll(e.schemaParseFailures);
                }
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, telepactSchemaNameToJson);
        }

        var headerKeys = new HashSet<String>();
        var responseHeaderKeys = new HashSet<String>();
        var errorKeys = new HashSet<String>();

        for (String schemaKey : schemaKeys) {
            if (schemaKey.startsWith("info.")) {
                continue;
            } else if (schemaKey.startsWith("headers.")) {
                headerKeys.add(schemaKey);
                continue;
            } else if (schemaKey.startsWith("errors.")) {
                errorKeys.add(schemaKey);
                continue;
            }

            var thisIndex = schemaKeysToIndex.get(schemaKey);
            var thisDocumentName = schemaKeysToDocumentName.get(schemaKey);

            try {
                getOrParseType(
                        List.of(thisIndex),
                        schemaKey,
                        new ParseContext(
                                thisDocumentName,
                                telepactSchemaNameToPseudoJson,
                                telepactSchemaNameToJson,
                                schemaKeysToDocumentName,
                                schemaKeysToIndex,
                                parsedTypes,
                                parseFailures,
                                failedTypes));
            } catch (TelepactSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, telepactSchemaNameToJson);
        }

        var errors = new ArrayList<VError>();

        for (String thisKey : errorKeys) {
            var thisIndex = schemaKeysToIndex.get(thisKey);
            var thisDocumentName = schemaKeysToDocumentName.get(thisKey);
            var telepactSchemaPseudoJson = telepactSchemaNameToPseudoJson.get(thisDocumentName);
            var def = (Map<String, Object>) telepactSchemaPseudoJson.get(thisIndex);

            try {
                var error = parseErrorType(
                        List.of(thisIndex),
                        def,
                        thisKey,
                        new ParseContext(
                                thisDocumentName,
                                telepactSchemaNameToPseudoJson,
                                telepactSchemaNameToJson,
                                schemaKeysToDocumentName,
                                schemaKeysToIndex,
                                parsedTypes,
                                parseFailures,
                                failedTypes));
                errors.add(error);
            } catch (TelepactSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, telepactSchemaNameToJson);
        }

        try {
            catchErrorCollisions(telepactSchemaNameToPseudoJson, errorKeys, schemaKeysToIndex, schemaKeysToDocumentName,
                    telepactSchemaNameToJson);
        } catch (TelepactSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, telepactSchemaNameToJson);
        }

        for (var error : errors) {
            try {
                applyErrorToParsedTypes(error, parsedTypes, schemaKeysToDocumentName, schemaKeysToIndex,
                        telepactSchemaNameToJson);
            } catch (TelepactSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        var headers = new ArrayList<VHeaders>();

        var requestHeaders = new HashMap<String, VFieldDeclaration>();
        var responseHeaders = new HashMap<String, VFieldDeclaration>();

        for (String headerKey : headerKeys) {
            var thisIndex = schemaKeysToIndex.get(headerKey);
            var thisDocumentName = schemaKeysToDocumentName.get(headerKey);
            var telepactSchemaPseudoJson = telepactSchemaNameToPseudoJson.get(thisDocumentName);
            var def = (Map<String, Object>) telepactSchemaPseudoJson.get(thisIndex);

            try {
                var headerType = parseHeadersType(
                        List.of(thisIndex),
                        def,
                        headerKey,
                        new ParseContext(
                                thisDocumentName,
                                telepactSchemaNameToPseudoJson,
                                telepactSchemaNameToJson,
                                schemaKeysToDocumentName,
                                schemaKeysToIndex,
                                parsedTypes,
                                parseFailures,
                                failedTypes));
                headers.add(headerType);
            } catch (TelepactSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, telepactSchemaNameToJson);
        }

        try {
            catchHeaderCollisions(
                    telepactSchemaNameToPseudoJson, headerKeys, schemaKeysToIndex, schemaKeysToDocumentName,
                    telepactSchemaNameToJson);
        } catch (TelepactSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, telepactSchemaNameToJson);
        }

        for (final var header : headers) {
            requestHeaders.putAll(header.requestHeaders);
            responseHeaders.putAll(header.responseHeaders);

        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, telepactSchemaNameToJson);
        }

        final var finalOriginalSchema = new ArrayList<>(originalSchema.values());

        return new TelepactSchema(
                finalOriginalSchema,
                parsedTypes,
                requestHeaders,
                responseHeaders);
    }
}
