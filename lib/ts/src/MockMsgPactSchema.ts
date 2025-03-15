import { VFieldDeclaration } from './internal/types/VFieldDeclaration';
import { VType } from './internal/types/VType';
import { createMockMsgPactSchemaFromFileJsonMap } from './internal/schema/CreateMockMsgPactSchemaFromFileJsonMap';
import { getSchemaFileMap } from './internal/schema/GetSchemaFileMap';
import { FsModule, PathModule } from './fileSystem';

export class MockMsgPactSchema {
    /**
     * A parsed msgPact schema.
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

    static fromJson(json: string): MockMsgPactSchema {
        return createMockMsgPactSchemaFromFileJsonMap({ auto_: json });
    }

    static fromFileJsonMap(jsonDocuments: Record<string, string>): MockMsgPactSchema {
        return createMockMsgPactSchemaFromFileJsonMap(jsonDocuments);
    }

    static fromDirectory(directory: string, fs: FsModule, path: PathModule): MockMsgPactSchema {
        const m = getSchemaFileMap(directory, fs, path);
        return createMockMsgPactSchemaFromFileJsonMap(m);
    }
}
