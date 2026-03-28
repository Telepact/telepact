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

import { getInternalTelepactJson } from './GetInternalTelepactJson';
import { getAuthTelepactJson } from './GetAuthTelepactJson';
import { TelepactSchema } from '../../TelepactSchema';
import { parseTelepactSchema } from './ParseTelepactSchema';
import { findSchemaKey } from './FindSchemaKey';
import { copyDocumentLocators } from './DocumentLocators';

export function createTelepactSchemaFromFileJsonMap(jsonDocuments: Record<string, string>): TelepactSchema {
    const finalJsonDocuments = { ...jsonDocuments };
    copyDocumentLocators(jsonDocuments, finalJsonDocuments);
    const internalTelepactJson = getInternalTelepactJson();
    if (!hasBundledDefinitions(jsonDocuments, 'internal_', internalTelepactJson)) {
        finalJsonDocuments['internal_'] = internalTelepactJson;
    }

    // Determine if we need to add the auth schema
    const authTelepactJson = getAuthTelepactJson();
    for (const json of Object.values(jsonDocuments)) {
        const regex = /"struct\.Auth_"\s*:/;
        if (regex.test(json)) {
            if (!hasBundledDefinitions(jsonDocuments, 'auth_', authTelepactJson)) {
                finalJsonDocuments['auth_'] = authTelepactJson;
            }
            break;
        }
    }

    const telepactSchema = parseTelepactSchema(finalJsonDocuments);

    return telepactSchema;
}

function hasBundledDefinitions(
    jsonDocuments: Record<string, string>,
    bundledDocumentName: string,
    bundledJson: string,
): boolean {
    const bundledKeys = collectSchemaKeys({ [bundledDocumentName]: bundledJson });
    if (bundledKeys === null) {
        return false;
    }

    const providedKeys = collectSchemaKeys(jsonDocuments);
    if (providedKeys === null) {
        return false;
    }

    return Array.from(bundledKeys).every((key) => providedKeys.has(key));
}

function collectSchemaKeys(jsonDocuments: Record<string, string>): Set<string> | null {
    const schemaKeys = new Set<string>();

    for (const [documentName, jsonValue] of Object.entries(jsonDocuments)) {
        let pseudoJson: unknown;
        try {
            pseudoJson = JSON.parse(jsonValue);
        } catch {
            return null;
        }

        if (!Array.isArray(pseudoJson)) {
            return null;
        }

        for (const [index, definition] of pseudoJson.entries()) {
            if (typeof definition !== 'object' || definition === null || Array.isArray(definition)) {
                continue;
            }

            try {
                const schemaKey = findSchemaKey(
                    documentName,
                    definition as Record<string, object>,
                    index,
                    jsonDocuments,
                );
                schemaKeys.add(schemaKey);
            } catch {
                return null;
            }
        }
    }

    return schemaKeys;
}
