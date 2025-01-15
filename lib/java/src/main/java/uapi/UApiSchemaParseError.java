package uapi;

import static uapi.internal.schema.MapSchemaParseFailuresToPseudoJson.mapSchemaParseFailuresToPseudoJson;

import java.util.List;
import java.util.Map;

import uapi.internal.schema.SchemaParseFailure;

/**
 * Indicates failure to parse a uAPI Schema.
 */
public class UApiSchemaParseError extends RuntimeException {

    public final List<SchemaParseFailure> schemaParseFailures;
    public final List<Object> schemaParseFailuresPseudoJson;

    public UApiSchemaParseError(List<SchemaParseFailure> schemaParseFailures, Map<String, String> documentNamesToJson) {
        super(String.valueOf(mapSchemaParseFailuresToPseudoJson(schemaParseFailures, documentNamesToJson)));
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(schemaParseFailures,
                documentNamesToJson);
    }

    public UApiSchemaParseError(List<SchemaParseFailure> schemaParseFailures, Map<String, String> documentNamesToJson,
            Throwable cause) {
        super(String.valueOf(mapSchemaParseFailuresToPseudoJson(schemaParseFailures, documentNamesToJson)), cause);
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(schemaParseFailures,
                documentNamesToJson);
    }
}