import { createMsgPactSchemaFromFileJsonMap } from './internal/schema/CreateMsgPactSchemaFromFileJsonMap';
import { getSchemaFileMap } from './internal/schema/GetSchemaFileMap';
import { VFieldDeclaration } from './internal/types/VFieldDeclaration';
import { VType } from './internal/types/VType';
import { FsModule, PathModule } from './fileSystem';

export class MsgPactSchema {
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

    static fromJson(json: string): MsgPactSchema {
        return createMsgPactSchemaFromFileJsonMap({ auto_: json });
    }

    static fromFileJsonMap(fileJsonMap: Record<string, string>): MsgPactSchema {
        return createMsgPactSchemaFromFileJsonMap(fileJsonMap);
    }

    /**
     * @param fs - node fs
     * @param path - node path
     */
    static fromDirectory(directory: string, fs: FsModule, path: PathModule): MsgPactSchema {
        // TODO
        const m = getSchemaFileMap(directory, fs, path);
        return createMsgPactSchemaFromFileJsonMap(m);
    }
}
