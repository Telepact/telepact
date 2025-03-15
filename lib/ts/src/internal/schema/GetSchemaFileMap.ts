import { FsModule, PathModule } from '../../fileSystem';

export function getSchemaFileMap(directory: string, fs: FsModule, path: PathModule): Record<string, string> {
    const finalJsonDocuments: Record<string, string> = {};

    const paths = fs.readdirSync(directory).map((file) => path.join(directory, file));
    for (const filePath of paths) {
        if (filePath.endsWith('.msgpact.json')) {
            const content = fs.readFileSync(filePath, 'utf-8');
            const relativePath = path.relative(directory, filePath);
            finalJsonDocuments[relativePath] = content;
        }
    }

    return finalJsonDocuments;
}
