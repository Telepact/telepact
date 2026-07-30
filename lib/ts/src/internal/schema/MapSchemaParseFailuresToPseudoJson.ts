//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure.js';
import { resolveDocumentCoordinates } from './DocumentLocators.js';

export function mapSchemaParseFailuresToPseudoJson(
    schemaParseFailures: SchemaParseFailure[],
    documentNamesToJson: Record<string, string>,
): any[] {
    const pseudoJsonList: any[] = [];
    for (const f of schemaParseFailures) {
        const location = resolveDocumentCoordinates(f.path, f.documentName, documentNamesToJson);
        const pseudoJson: any = {};
        pseudoJson.document = f.documentName;
        pseudoJson.location = location;
        pseudoJson.path = f.path;
        pseudoJson.reason = { [f.reason]: f.data };
        pseudoJsonList.push(Object.assign({}, pseudoJson));
    }
    return pseudoJsonList;
}
