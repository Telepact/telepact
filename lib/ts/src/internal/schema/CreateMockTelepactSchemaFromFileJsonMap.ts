//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { MockTelepactSchema } from '../../MockTelepactSchema.js';
import { createTelepactSchemaFromFileJsonMap } from './CreateTelepactSchemaFromFileJsonMap.js';
import { getMockTelepactJson } from './GetMockTelepactJson.js';
import { copyDocumentLocators } from './DocumentLocators.js';

export function createMockTelepactSchemaFromFileJsonMap(jsonDocuments: Record<string, string>): MockTelepactSchema {
    const finalJsonDocuments = { ...jsonDocuments };
    copyDocumentLocators(jsonDocuments, finalJsonDocuments);
    finalJsonDocuments['mock_'] = getMockTelepactJson();

    const telepactSchema = createTelepactSchemaFromFileJsonMap(finalJsonDocuments);

    return new MockTelepactSchema(
        telepactSchema.original,
        telepactSchema.full,
        telepactSchema.parsed,
        telepactSchema.parsedRequestHeaders,
        telepactSchema.parsedResponseHeaders,
    );
}
