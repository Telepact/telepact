package io.github.brenbar.uapi;

import java.util.List;

import io.github.brenbar.uapi.internal.SchemaParseFailure;

import static io.github.brenbar.uapi.internal.MapSchemaParseFailuresToPseudoJson.mapSchemaParseFailuresToPseudoJson;

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
}