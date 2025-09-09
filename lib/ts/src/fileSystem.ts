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

// Define the shape of the fs and path modules
export interface FsModule {
    readdirSync: (
        path: string | Buffer | URL,
        options?:
            | {
                  encoding: BufferEncoding | null;
                  withFileTypes?: false | undefined;
                  recursive?: boolean | undefined;
              }
            | BufferEncoding
            | null,
    ) => string[];
    readFileSync: (
        path: string | Buffer | URL | number,
        options:
            | {
                  encoding: BufferEncoding;
                  flag?: string | undefined;
              }
            | BufferEncoding,
    ) => string;
    statSync: (path: string | Buffer | URL) => { isDirectory: () => boolean };
}

export interface PathModule {
    join: (...paths: string[]) => string;
    relative: (from: string, to: string) => string;
}
