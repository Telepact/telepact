import { createTelepactSchemaFromFileJsonMap } from './internal/schema/CreateTelepactSchemaFromFileJsonMap';
import { getSchemaFileMap } from './internal/schema/GetSchemaFileMap';
import { VFieldDeclaration } from './internal/types/VFieldDeclaration';
import { VType } from './internal/types/VType';
import { FsModule, PathModule } from './fileSystem';

export class TelepactSchema {
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

    static fromJson(json: string): TelepactSchema {
        return createTelepactSchemaFromFileJsonMap({ auto_: json });
    }

    static fromFileJsonMap(fileJsonMap: Record<string, string>): TelepactSchema {
        return createTelepactSchemaFromFileJsonMap(fileJsonMap);
    }

    /**
     * @param fs - node fs
     * @param path - node path
     */
    static fromDirectory(directory: string, fs: FsModule, path: PathModule): TelepactSchema {
        // TODO
        const m = getSchemaFileMap(directory, fs, path);
        return createTelepactSchemaFromFileJsonMap(m);
    }
}
