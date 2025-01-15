import { SchemaParseFailure } from './internal/schema/SchemaParseFailure';
import { mapSchemaParseFailuresToPseudoJson } from './internal/schema/MapSchemaParseFailuresToPseudoJson';

export class UApiSchemaParseError extends Error {
    /**
     * Indicates failure to parse a uAPI Schema.
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
