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

// Define the minimal shape of the fs and path modules without depending on
// Node.js-only ambient types such as `Buffer` or `BufferEncoding`.
//
// This keeps the package declarations browser-safe while remaining
// structurally compatible with the standard Node `fs` and `path` modules.
export type FileSystemPath = string | URL;
export type FileSystemEncoding =
    | 'ascii'
    | 'utf8'
    | 'utf-8'
    | 'utf16le'
    | 'utf-16le'
    | 'ucs2'
    | 'ucs-2'
    | 'base64'
    | 'base64url'
    | 'latin1'
    | 'binary'
    | 'hex';

export interface FsModule {
    readdirSync: (
        path: FileSystemPath,
        options?:
            | {
                  encoding: FileSystemEncoding | null;
                  withFileTypes?: false | undefined;
                  recursive?: boolean | undefined;
              }
            | FileSystemEncoding
            | null,
    ) => string[];
    readFileSync: (
        path: FileSystemPath | number,
        options:
            | {
                  encoding: FileSystemEncoding;
                  flag?: string | undefined;
              }
            | FileSystemEncoding,
    ) => string;
    statSync: (path: FileSystemPath) => { isDirectory: () => boolean };
}

export interface PathModule {
    join: (...paths: string[]) => string;
    relative: (from: string, to: string) => string;
}
