//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { createTelepactSchemaFromFileJsonMap } from './internal/schema/CreateTelepactSchemaFromFileJsonMap.js';
import { getSchemaFileMap } from './internal/schema/GetSchemaFileMap.js';
import { TFieldDeclaration } from './internal/types/TFieldDeclaration.js';
import { TType } from './internal/types/TType.js';
import { FsModule, PathModule } from './fileSystem.js';

export class TelepactSchema {
    /**
     * A parsed telepact schema.
     */

    original: any[];
    full: any[];
    parsed: Record<string, TType>;
    parsedRequestHeaders: Record<string, TFieldDeclaration>;
    parsedResponseHeaders: Record<string, TFieldDeclaration>;

    constructor(
        original: any[],
        full: any[],
        parsed: Record<string, TType>,
        parsedRequestHeaders: Record<string, TFieldDeclaration>,
        parsedResponseHeaders: Record<string, TFieldDeclaration>,
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
