import { mapSchemaParseFailuresToPseudoJson } from "./_util";
import { _SchemaParseFailure } from "./_utilTypes";

/**
 * Indicates failure to parse a uAPI Schema.
 */
export class UApiSchemaParseError extends Error {
    public schemaParseFailures: _SchemaParseFailure[];
    public schemaParseFailuresPseudoJson: any[]; // adjust the type if you have a specific type for pseudo JSON

    /**
     * Creates an instance of UApiSchemaParseError with a cause.
     * @param {Array<_SchemaParseFailure>} schemaParseFailures List of schema parse failures.
     * @param {Error} cause The cause of the error.
     */
    constructor(schemaParseFailures: _SchemaParseFailure[], cause: Error | undefined = undefined) {
        super(JSON.stringify(mapSchemaParseFailuresToPseudoJson(schemaParseFailures), null, 2));
        this.name = this.constructor.name;
        this.schemaParseFailures = schemaParseFailures;
        this.schemaParseFailuresPseudoJson = mapSchemaParseFailuresToPseudoJson(schemaParseFailures);
        this.stack = cause ? cause.stack : this.stack; // Assigning cause stack to retain the stack trace.
    }
}
