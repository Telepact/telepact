package io.github.brenbar.uapi;

import java.util.List;

/**
 * Indicates failure to parse a uAPI Schema.
 */
public class UApiSchemaParseError extends RuntimeException {

    public final List<_SchemaParseFailure> schemaParseFailures;
    public final List<Object> schemaParseFailuresPseudoJson;

    public UApiSchemaParseError(List<_SchemaParseFailure> schemaParseFailures) {
        super(String.valueOf(_Util.mapSchemaParseFailuresToPseudoJson(schemaParseFailures)));
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = _Util.mapSchemaParseFailuresToPseudoJson(schemaParseFailures);
    }

    public UApiSchemaParseError(List<_SchemaParseFailure> schemaParseFailures, Throwable cause) {
        super(String.valueOf(_Util.mapSchemaParseFailuresToPseudoJson(schemaParseFailures)), cause);
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = _Util.mapSchemaParseFailuresToPseudoJson(schemaParseFailures);
    }
}