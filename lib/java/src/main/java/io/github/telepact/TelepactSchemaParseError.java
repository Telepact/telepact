//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
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