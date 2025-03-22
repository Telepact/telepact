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

import { TStruct } from '../types/TStruct';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { generateRandomStruct } from '../../internal/generation/GenerateRandomStruct';

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
