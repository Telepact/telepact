import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';
import { mapSchemaParseFailuresToPseudoJson } from 'uapi/internal/schema/MapSchemaParseFailuresToPseudoJson';

export class UApiSchemaParseError extends Error {
    /**
     * Indicates failure to parse a uAPI Schema.
     */

    public schemaParseFailures: SchemaParseFailure[];
    public schemaParseFailuresPseudoJson: any;

    constructor(schemaParseFailures: SchemaParseFailure[]) {
        super(mapSchemaParseFailuresToPseudoJson(schemaParseFailures).toString());
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(schemaParseFailures);
    }
}
