//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { FsModule, PathModule } from '../../fileSystem.js';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure.js';
import { TelepactSchemaParseError } from '../../TelepactSchemaParseError.js';
import { DocumentLocator, setDocumentLocators } from './DocumentLocators.js';
import { parseTelepactYaml } from './ParseTelepactYaml.js';

export function getSchemaFileMap(directory: string, fs: FsModule, path: PathModule): Record<string, string> {
    const finalJsonDocuments: Record<string, string> = {};
    const documentLocators: Record<string, DocumentLocator> = {};

    const schemaParseFailures: SchemaParseFailure[] = [];

    const paths = fs.readdirSync(directory)
        .sort()
        .map((file) => path.join(directory, file));
    for (const filePath of paths) {
        const relativePath = path.relative(directory, filePath);
        if (fs.statSync(filePath).isDirectory()) {
            schemaParseFailures.push(new SchemaParseFailure(relativePath, [], 'DirectoryDisallowed', {}));
            finalJsonDocuments[relativePath] = '[]';
            continue;
        }

        const content = fs.readFileSync(filePath, 'utf-8');
        if (filePath.endsWith('.telepact.json')) {
            finalJsonDocuments[relativePath] = content;
        } else if (filePath.endsWith('.telepact.yaml')) {
            try {
                const parsed = parseTelepactYaml(content);
                finalJsonDocuments[relativePath] = parsed.canonicalJsonText;
                if (parsed.locator !== undefined) {
                    documentLocators[relativePath] = parsed.locator;
                }
            } catch {
                finalJsonDocuments[relativePath] = '[]';
                schemaParseFailures.push(new SchemaParseFailure(relativePath, [], 'JsonInvalid', {}));
            }
        } else {
            finalJsonDocuments[relativePath] = content;
            schemaParseFailures.push(new SchemaParseFailure(relativePath, [], 'FileNamePatternInvalid', { expected: '*.telepact.json|*.telepact.yaml' }));
        }
    }

    setDocumentLocators(finalJsonDocuments, documentLocators);

    if (schemaParseFailures.length > 0) {
        throw new TelepactSchemaParseError(schemaParseFailures, finalJsonDocuments);
    }

    return finalJsonDocuments;
}
