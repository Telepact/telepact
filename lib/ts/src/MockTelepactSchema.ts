//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TFieldDeclaration } from './internal/types/TFieldDeclaration.js';
import { TType } from './internal/types/TType.js';
import { createMockTelepactSchemaFromFileJsonMap } from './internal/schema/CreateMockTelepactSchemaFromFileJsonMap.js';
import { getSchemaFileMap } from './internal/schema/GetSchemaFileMap.js';
import { FsModule, PathModule } from './fileSystem.js';

export class MockTelepactSchema {
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
