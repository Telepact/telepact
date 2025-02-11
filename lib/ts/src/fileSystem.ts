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
}

export interface PathModule {
    join: (...paths: string[]) => string;
    relative: (from: string, to: string) => string;
}
