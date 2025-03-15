package io.github.msgpact;

import static io.github.msgpact.internal.schema.MapSchemaParseFailuresToPseudoJson.mapSchemaParseFailuresToPseudoJson;

import java.util.List;
import java.util.Map;

import io.github.msgpact.internal.schema.SchemaParseFailure;

/**
 * Indicates failure to parse a msgPact Schema.
 */
public class MsgPactSchemaParseError extends RuntimeException {

    public final List<SchemaParseFailure> schemaParseFailures;
    public final List<Object> schemaParseFailuresPseudoJson;

    public MsgPactSchemaParseError(List<SchemaParseFailure> schemaParseFailures,
            Map<String, String> documentNamesToJson) {
        super(String.valueOf(mapSchemaParseFailuresToPseudoJson(schemaParseFailures, documentNamesToJson)));
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(schemaParseFailures,
                documentNamesToJson);
    }

    public MsgPactSchemaParseError(List<SchemaParseFailure> schemaParseFailures,
            Map<String, String> documentNamesToJson,
            Throwable cause) {
        super(String.valueOf(mapSchemaParseFailuresToPseudoJson(schemaParseFailures, documentNamesToJson)), cause);
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(schemaParseFailures,
                documentNamesToJson);
    }
}