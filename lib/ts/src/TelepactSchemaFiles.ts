//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { FsModule, PathModule } from './fileSystem.js';
import { getSchemaFileMap } from './internal/schema/GetSchemaFileMap.js';

export class TelepactSchemaFiles {
    filenamesToJson: Record<string, string>;

    constructor(directory: string, fs: FsModule, path: PathModule) {
        this.filenamesToJson = getSchemaFileMap(directory, fs, path);
    }
}
