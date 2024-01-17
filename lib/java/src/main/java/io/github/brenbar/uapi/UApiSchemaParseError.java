package io.github.brenbar.uapi;

import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * Indicates failure to parse a uAPI Schema.
 */
public class UApiSchemaParseError extends RuntimeException {

    public final List<SchemaParseFailure> schemaParseFailures;
    public final List<Object> schemaParseFailuresPseudoJson;

    public UApiSchemaParseError(List<SchemaParseFailure> schemaParseFailures) {
        super(String.valueOf(mapSchemaParseFailuresToPseudoJson(schemaParseFailures)));
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(schemaParseFailures);
    }

    public UApiSchemaParseError(List<SchemaParseFailure> schemaParseFailures, Throwable cause) {
        super(String.valueOf(mapSchemaParseFailuresToPseudoJson(schemaParseFailures)), cause);
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(schemaParseFailures);
    }

    private static List<Object> mapSchemaParseFailuresToPseudoJson(
            List<SchemaParseFailure> schemaParseFailures) {
        return (List<Object>) schemaParseFailures.stream()
                .map(f -> (Object) new TreeMap<>(Map.of("path", f.path, "reason", Map.of(f.reason, f.data))))
                .toList();
    }
}