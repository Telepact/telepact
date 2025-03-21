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

import { VFieldDeclaration } from '../types/VFieldDeclaration';
import { GenerateContext } from '../../internal/generation/GenerateContext';

export function generateRandomStruct(
    blueprintValue: any,
    useBlueprintValue: boolean,
    referenceStruct: { [key: string]: VFieldDeclaration },
    ctx: GenerateContext,
): any {
    const startingStruct = useBlueprintValue ? blueprintValue : {};

    const sortedReferenceStruct = Array.from(Object.entries(referenceStruct)).sort((e1, e2) => {
        const a = e1[0];
        const b = e2[0];
        for (let i = 0; i < Math.min(a.length, b.length); i++) {
            const charCodeA = a.charCodeAt(i);
            const charCodeB = b.charCodeAt(i);
            if (charCodeA !== charCodeB) {
                // If the characters are different, return the comparison result
                // where lowercase letters are considered greater than uppercase letters
                return charCodeA - charCodeB;
            }
        }
        // If one string is a prefix of the other, the shorter string comes first
        return a.length - b.length;
    });

    const obj: Record<string, any> = {};
    for (const [fieldName, fieldDeclaration] of sortedReferenceStruct) {
        const thisBlueprintValue = startingStruct[fieldName];
        const thisUseBlueprintValue = fieldName in startingStruct;
        const typeDeclaration = fieldDeclaration.typeDeclaration;

        let value: any;
        if (thisUseBlueprintValue) {
            value = typeDeclaration.generateRandomValue(thisBlueprintValue, thisUseBlueprintValue, ctx);
        } else {
            if (!fieldDeclaration.optional) {
                if (!ctx.alwaysIncludeRequiredFields && ctx.randomGenerator.nextBoolean()) {
                    continue;
                }
                value = typeDeclaration.generateRandomValue(null, false, ctx);
            } else {
                if (!ctx.includeOptionalFields || (ctx.randomizeOptionalFields && ctx.randomGenerator.nextBoolean())) {
                    continue;
                }
                value = typeDeclaration.generateRandomValue(null, false, ctx);
            }
        }

        obj[fieldName] = value;
    }

    return obj;
}
