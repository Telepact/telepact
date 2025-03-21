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

import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { getPathDocumentCoordinatesPseudoJson } from './GetPathDocumentCoordinatesPseudoJson';

export function mapSchemaParseFailuresToPseudoJson(
    schemaParseFailures: SchemaParseFailure[],
    documentNamesToJson: Record<string, string>,
): any[] {
    const pseudoJsonList: any[] = [];
    for (const f of schemaParseFailures) {
        const documentJson = documentNamesToJson[f.documentName];
        const location = getPathDocumentCoordinatesPseudoJson(f.path, documentJson);
        const pseudoJson: any = {};
        pseudoJson.document = f.documentName;
        pseudoJson.location = location;
        pseudoJson.path = f.path;
        pseudoJson.reason = { [f.reason]: f.data };
        pseudoJsonList.push(Object.assign({}, pseudoJson));
    }
    return pseudoJsonList;
}
