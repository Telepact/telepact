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

import { FsModule, PathModule } from '../../fileSystem';

export function getSchemaFileMap(directory: string, fs: FsModule, path: PathModule): Record<string, string> {
    const finalJsonDocuments: Record<string, string> = {};

    const paths = fs.readdirSync(directory).map((file) => path.join(directory, file));
    for (const filePath of paths) {
        if (filePath.endsWith('.telepact.json')) {
            const content = fs.readFileSync(filePath, 'utf-8');
            const relativePath = path.relative(directory, filePath);
            finalJsonDocuments[relativePath] = content;
        }
    }

    return finalJsonDocuments;
}
