package io.github.telepact;

import static io.github.telepact.internal.schema.MapSchemaParseFailuresToPseudoJson.mapSchemaParseFailuresToPseudoJson;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.schema.SchemaParseFailure;

/**
 * Indicates failure to parse a telepact Schema.
 */
public class TelepactSchemaParseError extends RuntimeException {

    public final List<SchemaParseFailure> schemaParseFailures;
    public final List<Object> schemaParseFailuresPseudoJson;

    public TelepactSchemaParseError(List<SchemaParseFailure> schemaParseFailures,
            Map<String, String> documentNamesToJson) {
        super(String.valueOf(mapSchemaParseFailuresToPseudoJson(schemaParseFailures, documentNamesToJson)));
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(schemaParseFailures,
                documentNamesToJson);
    }

    public TelepactSchemaParseError(List<SchemaParseFailure> schemaParseFailures,
            Map<String, String> documentNamesToJson,
            Throwable cause) {
        super(String.valueOf(mapSchemaParseFailuresToPseudoJson(schemaParseFailures, documentNamesToJson)), cause);
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(schemaParseFailures,
                documentNamesToJson);
    }
}