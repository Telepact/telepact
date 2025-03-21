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

import { TelepactSchemaParseError } from '../../TelepactSchemaParseError';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { getPathDocumentCoordinatesPseudoJson } from '../../internal/schema/GetPathDocumentCoordinatesPseudoJson';

export function catchErrorCollisions(
    telepactSchemaNameToPseudoJson: Record<string, any[]>,
    errorKeys: Set<string>,
    keysToIndex: Record<string, number>,
    schemaKeysToDocumentNames: Record<string, string>,
    documentNamesToJson: Record<string, string>,
): void {
    const parseFailures: SchemaParseFailure[] = [];

    const errorKeysList = [...errorKeys];

    errorKeysList.sort((k1, k2) => {
        const documentName1 = schemaKeysToDocumentNames[k1];
        const documentName2 = schemaKeysToDocumentNames[k2];
        if (documentName1 !== documentName2) {
            return documentName1.localeCompare(documentName2);
        } else {
            const index1 = keysToIndex[k1];
            const index2 = keysToIndex[k2];
            return index1 - index2;
        }
    });

    for (let i = 0; i < errorKeysList.length; i++) {
        for (let j = i + 1; j < errorKeysList.length; j++) {
            const defKey = errorKeysList[i];
            const otherDefKey = errorKeysList[j];

            const index = keysToIndex[defKey];
            const otherIndex = keysToIndex[otherDefKey];

            const documentName = schemaKeysToDocumentNames[defKey];
            const otherDocumentName = schemaKeysToDocumentNames[otherDefKey];

            const telepactSchemaPseudoJson = telepactSchemaNameToPseudoJson[documentName];
            const otherTelepactSchemaPseudoJson = telepactSchemaNameToPseudoJson[otherDocumentName];

            const def = telepactSchemaPseudoJson[index] as Record<string, object>;
            const otherDef = otherTelepactSchemaPseudoJson[otherIndex] as Record<string, object>;

            const errDef = def[defKey] as object[];
            const otherErrDef = otherDef[otherDefKey] as object[];

            for (let k = 0; k < errDef.length; k++) {
                const thisErrDef = errDef[k] as Record<string, object>;
                const thisErrDefKeys = new Set(Object.keys(thisErrDef));
                thisErrDefKeys.delete('///');

                for (let l = 0; l < otherErrDef.length; l++) {
                    const thisOtherErrDef = otherErrDef[l] as Record<string, object>;
                    const thisOtherErrDefKeys = new Set(Object.keys(thisOtherErrDef));
                    thisOtherErrDefKeys.delete('///');

                    if (
                        thisErrDefKeys.size === thisOtherErrDefKeys.size &&
                        [...thisErrDefKeys].every((key) => thisOtherErrDefKeys.has(key))
                    ) {
                        const thisErrorDefKey = thisErrDefKeys.values().next().value as string;
                        const thisOtherErrorDefKey = thisOtherErrDefKeys.values().next().value as string;
                        const thisPath = [index, defKey, k, thisErrorDefKey];
                        const thisDocumentJson = documentNamesToJson[documentName];
                        const thisLocation = getPathDocumentCoordinatesPseudoJson(thisPath, thisDocumentJson);
                        parseFailures.push(
                            new SchemaParseFailure(
                                otherDocumentName,
                                [otherIndex, otherDefKey, l, thisOtherErrorDefKey],
                                'PathCollision',
                                { document: documentName, path: thisPath, location: thisLocation },
                            ),
                        );
                    }
                }
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, documentNamesToJson);
    }
}
