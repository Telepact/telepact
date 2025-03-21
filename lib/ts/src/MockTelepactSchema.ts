//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

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
