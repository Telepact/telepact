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

export function findSchemaKey(
    documentName: string,
    definition: Record<string, any>,
    index: number,
    documentNamesToJson: Record<string, string>,
): string {
    const regex = /^(((fn|errors|headers|info)|((struct|union|_ext)(<[0-2]>)?))\..*)/;
    const matches: string[] = [];

    const keys = Object.keys(definition).sort();

    for (const e of keys) {
        if (regex.test(e)) {
            matches.push(e);
        }
    }

    if (matches.length === 1) {
        return matches[0];
    } else {
        const parseFailure = new SchemaParseFailure(documentName, [index], 'ObjectKeyRegexMatchCountUnexpected', {
            regex: regex.toString().slice(1, -1),
            actual: matches.length,
            expected: 1,
            keys: keys,
        });
        throw new TelepactSchemaParseError([parseFailure], documentNamesToJson);
    }
}
