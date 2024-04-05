import { extendUApiSchema, newUApiSchema } from './_util';
import { _UFieldDeclaration, _UType } from './_utilTypes';

/**
 * A parsed uAPI schema.
 */
export class UApiSchema {
    original: any[];
    parsed: Record<string, _UType>;
    parsedRequestHeaders: Record<string, _UFieldDeclaration>;
    parsedResponseHeaders: Record<string, _UFieldDeclaration>;
    typeExtensions: Record<string, _UType>;

    constructor(
        original: any[],
        parsed: Record<string, _UType>,
        parsedRequestHeaders: Record<string, _UFieldDeclaration>,
        parsedResponseHeaders: Record<string, _UFieldDeclaration>,
        typeExtensions: Record<string, _UType>
    ) {
        this.original = original;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
        this.typeExtensions = typeExtensions;
    }

    /**
     * Creates a UApiSchema instance from JSON string.
     * @param json The JSON string to parse.
     * @returns A UApiSchema instance.
     */
    static fromJson(json: string): UApiSchema {
        return newUApiSchema(json, {});
    }

    /**
     * Extends an existing UApiSchema with additional JSON.
     * @param base The base UApiSchema to extend.
     * @param json The JSON string to extend with.
     * @returns An extended UApiSchema instance.
     */
    static extend(base: UApiSchema, json: string): UApiSchema {
        return extendUApiSchema(base, json, {});
    }
}
