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

import { createTelepactSchemaFromFileJsonMap } from './internal/schema/CreateTelepactSchemaFromFileJsonMap';
import { getSchemaFileMap } from './internal/schema/GetSchemaFileMap';
import { TFieldDeclaration } from './internal/types/TFieldDeclaration';
import { TType } from './internal/types/TType';
import { FsModule, PathModule } from './fileSystem';

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
