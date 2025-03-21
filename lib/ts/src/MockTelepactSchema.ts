import { VFieldDeclaration } from './internal/types/VFieldDeclaration';
import { VType } from './internal/types/VType';
import { createMockTelepactSchemaFromFileJsonMap } from './internal/schema/CreateMockTelepactSchemaFromFileJsonMap';
import { getSchemaFileMap } from './internal/schema/GetSchemaFileMap';
import { FsModule, PathModule } from './fileSystem';

export class MockTelepactSchema {
    /**
     * A parsed telepact schema.
     */

    original: any[];
    full: any[];
    parsed: Record<string, VType>;
    parsedRequestHeaders: Record<string, VFieldDeclaration>;
    parsedResponseHeaders: Record<string, VFieldDeclaration>;

    constructor(
        original: any[],
        full: any[],
        parsed: Record<string, VType>,
        parsedRequestHeaders: Record<string, VFieldDeclaration>,
        parsedResponseHeaders: Record<string, VFieldDeclaration>,
    ) {
        this.original = original;
        this.full = full;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
    }

    static fromJson(json: string): MockTelepactSchema {
        return createMockTelepactSchemaFromFileJsonMap({ auto_: json });
    }

    static fromFileJsonMap(jsonDocuments: Record<string, string>): MockTelepactSchema {
        return createMockTelepactSchemaFromFileJsonMap(jsonDocuments);
    }

    static fromDirectory(directory: string, fs: FsModule, path: PathModule): MockTelepactSchema {
        const m = getSchemaFileMap(directory, fs, path);
        return createMockTelepactSchemaFromFileJsonMap(m);
    }
}
