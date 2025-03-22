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

import { TError } from '../types/TError';
import { TType } from '../types/TType';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { TelepactSchemaParseError } from '../../TelepactSchemaParseError';
import { TFn } from '../types/TFn';
import { getPathDocumentCoordinatesPseudoJson } from '../../internal/schema/GetPathDocumentCoordinatesPseudoJson';

export function applyErrorToParsedTypes(
    error: TError,
    parsedTypes: { [key: string]: TType },
    schemaKeysToDocumentNames: { [key: string]: string },
    schemaKeysToIndex: { [key: string]: number },
    documentNamesToJson: { [key: string]: string },
): void {
    const parseFailures: SchemaParseFailure[] = [];

    const errorKey = error.name;
    const errorIndex = schemaKeysToIndex[errorKey];
    const documentName = schemaKeysToDocumentNames[errorKey];

    for (const parsedTypeName in parsedTypes) {
        const parsedType = parsedTypes[parsedTypeName];

        if (!(parsedType instanceof TFn)) {
            continue;
        }

        const f = parsedType;
        const fnName = f.name;
        const regex = new RegExp(f.errorsRegex);
        const fnResult = f.result;
        const fnResultTags = fnResult.tags;
        const errorErrors = error.errors;
        const errorTags = errorErrors.tags;

        const matcher = regex.exec(errorKey);

        if (!matcher) {
            continue;
        }

        for (const errorTagName in errorTags) {
            const errorTag = errorTags[errorTagName];
            const newKey = errorTagName;

            if (newKey in fnResultTags) {
                const otherPathIndex = schemaKeysToIndex[fnName];
                const errorTagIndex = error.errors.tagIndices[newKey];
                const otherDocumentName = schemaKeysToDocumentNames[fnName];
                const fnErrorTagIndex = f.result.tagIndices[newKey];
                const otherPath = [otherPathIndex, '->', fnErrorTagIndex, newKey];
                const otherDocumentJson = documentNamesToJson[otherDocumentName];
                const otherLocation = getPathDocumentCoordinatesPseudoJson(otherPath, otherDocumentJson);
                parseFailures.push(
                    new SchemaParseFailure(
                        documentName,
                        [errorIndex, errorKey, errorTagIndex, newKey],
                        'PathCollision',
                        { document: otherDocumentName, path: otherPath, location: otherLocation },
                    ),
                );
            }

            fnResultTags[newKey] = errorTag;
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, documentNamesToJson);
    }
}
