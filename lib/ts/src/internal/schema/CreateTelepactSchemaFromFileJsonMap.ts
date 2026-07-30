//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { getInternalTelepactJson } from './GetInternalTelepactJson.js';
import { getAuthTelepactJson } from './GetAuthTelepactJson.js';
import { TelepactSchema } from '../../TelepactSchema.js';
import { parseTelepactSchema } from './ParseTelepactSchema.js';
import { findSchemaKey } from './FindSchemaKey.js';
import { copyDocumentLocators } from './DocumentLocators.js';

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
        const regex = /"union\.Auth_"\s*:/;
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
