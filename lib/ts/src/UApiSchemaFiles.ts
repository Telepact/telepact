import { getSchemaFileMap } from './internal/schema/GetSchemaFileMap';

export class UApiSchemaFiles {
    filenamesToJson: Record<string, string>;

    constructor(directory: string) {
        this.filenamesToJson = getSchemaFileMap(directory);
    }
}
