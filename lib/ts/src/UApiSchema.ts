import { UFieldDeclaration } from './internal/types/UFieldDeclaration';
import { UType } from './internal/types/UType';
import { newUapiSchema } from './internal/schema/NewUApiSchema';
import { extendUapiSchema } from './internal/schema/ExtendUApiSchema';

export class UApiSchema {
    /**
     * A parsed uAPI schema.
     */

    original: any[];
    parsed: Record<string, UType>;
    parsedRequestHeaders: Record<string, UFieldDeclaration>;
    parsedResponseHeaders: Record<string, UFieldDeclaration>;

    constructor(
        original: any[],
        parsed: Record<string, UType>,
        parsedRequestHeaders: Record<string, UFieldDeclaration>,
        parsedResponseHeaders: Record<string, UFieldDeclaration>,
    ) {
        this.original = original;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
    }

    static fromJson(json: string): UApiSchema {
        return newUapiSchema(json);
    }

    static extend(base: UApiSchema, json: string): UApiSchema {
        return extendUapiSchema(base, json);
    }
}
