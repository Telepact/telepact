import { UFieldDeclaration } from './internal/types/UFieldDeclaration';
import { UType } from './internal/types/UType';
import { createMockUApiSchemaFromFileJsonMap } from './internal/schema/CreateMockUApiSchemaFromFileJsonMap';
import { getSchemaFileMap } from './internal/schema/GetSchemaFileMap';

export class MockUApiSchema {
    /**
     * A parsed uAPI schema.
     */

    original: any[];
    full: any[];
    parsed: Record<string, UType>;
    parsedRequestHeaders: Record<string, UFieldDeclaration>;
    parsedResponseHeaders: Record<string, UFieldDeclaration>;

    constructor(
        original: any[],
        full: any[],
        parsed: Record<string, UType>,
        parsedRequestHeaders: Record<string, UFieldDeclaration>,
        parsedResponseHeaders: Record<string, UFieldDeclaration>,
    ) {
        this.original = original;
        this.full = full;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
    }

    static fromJson(json: string): MockUApiSchema {
        return createMockUApiSchemaFromFileJsonMap({ auto_: json });
    }

    static fromFileJsonMap(jsonDocuments: Record<string, string>): MockUApiSchema {
        return createMockUApiSchemaFromFileJsonMap(jsonDocuments);
    }

    static fromDirectory(directory: string): MockUApiSchema {
        const m = getSchemaFileMap(directory);
        return createMockUApiSchemaFromFileJsonMap(m);
    }
}
