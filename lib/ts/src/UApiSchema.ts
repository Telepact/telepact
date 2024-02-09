import { extendUApiSchema, newUApiSchema } from "./_util";
import { _UType } from "./_utilTypes";

/**
 * A parsed uAPI schema.
 */
export class UApiSchema {
    original: any[];
    parsed: Record<string, _UType>;
    typeExtensions: Record<string, _UType>;

    constructor(original: any[], parsed: Record<string, _UType>, typeExtensions: Record<string, _UType>) {
        this.original = original;
        this.parsed = parsed;
        this.typeExtensions = typeExtensions;
    }

    /**
     * Creates a UApiSchema instance from JSON string.
     * @param json The JSON string to parse.
     * @returns A UApiSchema instance.
     */
    static fromJson(json: string): UApiSchema {
        return newUApiSchema(json, new Map());
    }

    /**
     * Extends an existing UApiSchema with additional JSON.
     * @param base The base UApiSchema to extend.
     * @param json The JSON string to extend with.
     * @returns An extended UApiSchema instance.
     */
    static extend(base: UApiSchema, json: string): UApiSchema {
        return extendUApiSchema(base, json, new Map());
    }

    /**
     * Creates a UApiSchema instance from JSON string with type extensions.
     * @param json The JSON string to parse.
     * @param typeExtensions Map of type extensions.
     * @returns A UApiSchema instance with type extensions.
     */
    static fromJsonWithExtensions(json: string, typeExtensions: Map<string, _UType>): UApiSchema {
        return newUApiSchema(json, typeExtensions);
    }

    /**
     * Extends an existing UApiSchema with additional JSON and type extensions.
     * @param base The base UApiSchema to extend.
     * @param json The JSON string to extend with.
     * @param typeExtensions Map of type extensions.
     * @returns An extended UApiSchema instance with type extensions.
     */
    static extendWithExtensions(base: UApiSchema, json: string, typeExtensions: Map<string, _UType>): UApiSchema {
        return extendUApiSchema(base, json, typeExtensions);
    }
}
