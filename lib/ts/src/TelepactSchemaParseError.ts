//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { SchemaParseFailure } from './internal/schema/SchemaParseFailure.js';
import { mapSchemaParseFailuresToPseudoJson } from './internal/schema/MapSchemaParseFailuresToPseudoJson.js';

export class TelepactSchemaParseError extends Error {
    /**
     * Indicates failure to parse a telepact Schema.
     */

    public schemaParseFailures: SchemaParseFailure[];
    public schemaParseFailuresPseudoJson: any;

    constructor(schemaParseFailures: SchemaParseFailure[], documentNamesToJson: Record<string, string>, cause?: Error) {
        super(JSON.stringify(mapSchemaParseFailuresToPseudoJson(schemaParseFailures, documentNamesToJson), null, 2), {
            cause: cause,
        });
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(
            schemaParseFailures,
            documentNamesToJson,
        );
    }
}
