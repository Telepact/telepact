import { FsModule, PathModule } from './fileSystem';
import { getSchemaFileMap } from './internal/schema/GetSchemaFileMap';

export class TelepactSchemaFiles {
    filenamesToJson: Record<string, string>;

    constructor(directory: string, fs: FsModule, path: PathModule) {
        this.filenamesToJson = getSchemaFileMap(directory, fs, path);
    }
}
