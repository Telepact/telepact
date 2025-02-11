import { createUApiSchemaFromFileJsonMap } from './internal/schema/CreateUApiSchemaFromFileJsonMap';
import { getSchemaFileMap } from './internal/schema/GetSchemaFileMap';
import { UFieldDeclaration } from './internal/types/UFieldDeclaration';
import { UType } from './internal/types/UType';
import { FsModule, PathModule } from './fileSystem';

export class UApiSchema {
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

    static fromJson(json: string): UApiSchema {
        return createUApiSchemaFromFileJsonMap({ auto_: json });
    }

    static fromFileJsonMap(fileJsonMap: Record<string, string>): UApiSchema {
        return createUApiSchemaFromFileJsonMap(fileJsonMap);
    }

    /**
     * @param fs - node fs
     * @param path - node path
     */
    static fromDirectory(directory: string, fs: FsModule, path: PathModule): UApiSchema {
        // TODO
        const m = getSchemaFileMap(directory, fs, path);
        return createUApiSchemaFromFileJsonMap(m);
    }
}
