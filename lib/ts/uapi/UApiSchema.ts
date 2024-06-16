import { UFieldDeclaration } from 'uapi/internal/types/UFieldDeclaration';
import { UType } from 'uapi/internal/types/UType';
import { newUApiSchema } from 'uapi/internal/schema/NewUApiSchema';
import { extendUApiSchema } from 'uapi/internal/schema/ExtendUApiSchema';

export class UApiSchema {
    /**
     * A parsed uAPI schema.
     */

    original: any[];
    parsed: Record<string, UType>;
    parsedRequestHeaders: Record<string, UFieldDeclaration>;
    parsedResponseHeaders: Record<string, UFieldDeclaration>;
    typeExtensions: Record<string, UType>;

    constructor(
        original: any[],
        parsed: Record<string, UType>,
        parsedRequestHeaders: Record<string, UFieldDeclaration>,
        parsedResponseHeaders: Record<string, UFieldDeclaration>,
        typeExtensions: Record<string, UType>,
    ) {
        this.original = original;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
        this.typeExtensions = typeExtensions;
    }

    static fromJson(json: string): UApiSchema {
        return newUApiSchema(json, {});
    }

    static extend(base: UApiSchema, json: string): UApiSchema {
        return extendUApiSchema(base, json, {});
    }
}
