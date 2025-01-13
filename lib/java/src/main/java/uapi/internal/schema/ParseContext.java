package uapi.internal.schema;

import java.util.List;
import java.util.Map;
import java.util.Set;

import uapi.internal.types.UType;

public class ParseContext {

    public final String documentName;
    public final List<Object> path;
    public final Map<String, List<Object>> uApiSchemaDocumentsToPseudoJson;
    public final Map<String, String> schemaKeysToDocumentName;
    public final Map<String, Integer> schemaKeysToIndex;
    public final Map<String, UType> parsedTypes;
    public final List<SchemaParseFailure> allParseFailures;
    public final Set<String> failedTypes;

    public ParseContext(String documentName,
            List<Object> path,
            Map<String, List<Object>> uApiSchemaDocumentsToPseudoJson,
            Map<String, String> schemaKeysToDocumentName, Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        this.documentName = documentName;
        this.path = path;
        this.uApiSchemaDocumentsToPseudoJson = uApiSchemaDocumentsToPseudoJson;
        this.schemaKeysToDocumentName = schemaKeysToDocumentName;
        this.schemaKeysToIndex = schemaKeysToIndex;
        this.parsedTypes = parsedTypes;
        this.allParseFailures = allParseFailures;
        this.failedTypes = failedTypes;
    }

    public ParseContext copyWithNewDocumentName(String documentName) {
        return new ParseContext(documentName, path, uApiSchemaDocumentsToPseudoJson, schemaKeysToDocumentName,
                schemaKeysToIndex, parsedTypes, allParseFailures, failedTypes);
    }

    public ParseContext copyWithNewPath(List<Object> path) {
        return new ParseContext(documentName, path, uApiSchemaDocumentsToPseudoJson, schemaKeysToDocumentName,
                schemaKeysToIndex, parsedTypes, allParseFailures, failedTypes);
    }

    public ParseContext copyWithNewDocumentNameAndPath(String documentName, List<Object> path) {
        return new ParseContext(documentName, path, uApiSchemaDocumentsToPseudoJson, schemaKeysToDocumentName,
                schemaKeysToIndex, parsedTypes, allParseFailures, failedTypes);
    }
}
