//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
