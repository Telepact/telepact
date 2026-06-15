//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TStruct } from '../types/TStruct.js';
import { GenerateContext } from '../../internal/generation/GenerateContext.js';
import { generateRandomStruct } from '../../internal/generation/GenerateRandomStruct.js';

export function generateRandomUnion(
    blueprintValue: any,
    useBlueprintValue: boolean,
    unionTagsReference: { [key: string]: TStruct },
    ctx: GenerateContext,
): any {
    if (!useBlueprintValue) {
        const sortedUnionTagsReference = Object.entries(unionTagsReference).sort((a, b) => a[0].localeCompare(b[0]));
        const randomIndex = ctx.randomGenerator.nextIntWithCeiling(sortedUnionTagsReference.length);
        const [unionTag, unionData] = sortedUnionTagsReference[randomIndex];
        return {
            [unionTag]: generateRandomStruct(null, false, unionData.fields, ctx),
        };
    } else {
        const startingUnion: Record<string, any> = blueprintValue;
        const [unionTag, unionStartingStruct] = Object.entries(startingUnion)[0];
        const unionStructType = unionTagsReference[unionTag];
        return {
            [unionTag]: generateRandomStruct(unionStartingStruct, true, unionStructType.fields, ctx),
        };
    }
}
