//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact;

import static io.github.telepact.internal.schema.MapSchemaParseFailuresToPseudoJson.mapSchemaParseFailuresToPseudoJson;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.schema.SchemaParseFailure;

/**
 * Indicates failure to parse a telepact Schema.
 */
public class TelepactSchemaParseError extends RuntimeException {

    /**
     * The list of schema parse failures.
     */
    public final List<SchemaParseFailure> schemaParseFailures;

    /**
     * The pseudo-JSON representation of schema parse failures.
     */
    public final List<Object> schemaParseFailuresPseudoJson;

    /**
     * Constructs a new TelepactSchemaParseError with the specified parameters.
     *
     * @param schemaParseFailures the list of schema parse failures
     * @param documentNamesToJson the pseudo-JSON representation of schema parse failures
     */
    public TelepactSchemaParseError(List<SchemaParseFailure> schemaParseFailures,
            Map<String, String> documentNamesToJson) {
        super(String.valueOf(mapSchemaParseFailuresToPseudoJson(schemaParseFailures, documentNamesToJson)));
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(schemaParseFailures,
                documentNamesToJson);
    }

    /**
     * Constructs a new TelepactSchemaParseError with the specified parameters and cause.
     *
     * @param schemaParseFailures the list of schema parse failures
     * @param documentNamesToJson the pseudo-JSON representation of schema parse failures
     * @param cause the cause of the error
     */
    public TelepactSchemaParseError(List<SchemaParseFailure> schemaParseFailures,
            Map<String, String> documentNamesToJson,
            Throwable cause) {
        super(String.valueOf(mapSchemaParseFailuresToPseudoJson(schemaParseFailures, documentNamesToJson)), cause);
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(schemaParseFailures,
                documentNamesToJson);
    }
}