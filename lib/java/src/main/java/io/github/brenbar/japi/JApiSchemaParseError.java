package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Indicates a failure to parse a jAPI Schema.
 */
public class JApiSchemaParseError extends RuntimeException {

    public final List<SchemaParseFailure> schemaParseFailures;

    public JApiSchemaParseError(List<SchemaParseFailure> schemaParseFailures) {
        super(mapSchemaParseFailuresToJson(schemaParseFailures));
        this.schemaParseFailures = schemaParseFailures;
    }

    public JApiSchemaParseError(List<SchemaParseFailure> schemaParseFailures, Throwable cause) {
        super(mapSchemaParseFailuresToJson(schemaParseFailures), cause);
        this.schemaParseFailures = schemaParseFailures;
    }

    private static String mapSchemaParseFailuresToJson(List<SchemaParseFailure> schemaParseFailures) {
        var pseudoJson = schemaParseFailures.stream()
                .map(f -> Map.of("path", f.path, "reason", Map.of(f.reason, f.data))).toList();
        try {
            return new ObjectMapper().writeValueAsString(pseudoJson);
        } catch (JsonProcessingException e) {
            return "UnknownSchemaParseFailure";
        }
    }
}