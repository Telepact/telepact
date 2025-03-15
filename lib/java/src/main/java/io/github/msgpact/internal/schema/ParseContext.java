package io.github.msgpact.internal.schema;

import java.util.List;
import java.util.Map;
import java.util.Set;

import io.github.msgpact.internal.types.VType;

public class ParseContext {

    public final String documentName;
    public final Map<String, List<Object>> msgPactSchemaDocumentsToPseudoJson;
    public final Map<String, String> msgPactSchemaDocumentNamesToJson;
    public final Map<String, String> schemaKeysToDocumentName;
    public final Map<String, Integer> schemaKeysToIndex;
    public final Map<String, VType> parsedTypes;
    public final List<SchemaParseFailure> allParseFailures;
    public final Set<String> failedTypes;

    public ParseContext(String documentName,
            Map<String, List<Object>> msgPactSchemaDocumentsToPseudoJson,
            Map<String, String> msgPactSchemaDocumentNamesToJson,
            Map<String, String> schemaKeysToDocumentName, Map<String, Integer> schemaKeysToIndex,
            Map<String, VType> parsedTypes,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        this.documentName = documentName;
        this.msgPactSchemaDocumentsToPseudoJson = msgPactSchemaDocumentsToPseudoJson;
        this.msgPactSchemaDocumentNamesToJson = msgPactSchemaDocumentNamesToJson;
        this.schemaKeysToDocumentName = schemaKeysToDocumentName;
        this.schemaKeysToIndex = schemaKeysToIndex;
        this.parsedTypes = parsedTypes;
        this.allParseFailures = allParseFailures;
        this.failedTypes = failedTypes;
    }

    public ParseContext copyWithNewDocumentName(String documentName) {
        return new ParseContext(documentName, msgPactSchemaDocumentsToPseudoJson, msgPactSchemaDocumentNamesToJson,
                schemaKeysToDocumentName,
                schemaKeysToIndex, parsedTypes, allParseFailures, failedTypes);
    }
}
