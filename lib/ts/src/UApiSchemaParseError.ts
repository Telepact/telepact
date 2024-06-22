import { SchemaParseFailure } from './internal/schema/SchemaParseFailure';
import { mapSchemaParseFailuresToPseudoJson } from './internal/schema/MapSchemaParseFailuresToPseudoJson';

export class UApiSchemaParseError extends Error {
    /**
     * Indicates failure to parse a uAPI Schema.
     */

    public schemaParseFailures: SchemaParseFailure[];
    public schemaParseFailuresPseudoJson: any;

    constructor(schemaParseFailures: SchemaParseFailure[], cause?: Error) {
        super(mapSchemaParseFailuresToPseudoJson(schemaParseFailures).toString(), { cause: cause });
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(schemaParseFailures);
    }
}
