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

import { GenerateContext } from '../../internal/generation/GenerateContext';
import { VTypeDeclaration } from '../types/VTypeDeclaration';

export function generateRandomArray(
    blueprintValue: any,
    useBlueprintValue: boolean,
    typeParameters: VTypeDeclaration[],
    ctx: GenerateContext,
): any[] {
    const nestedTypeDeclaration = typeParameters[0];

    if (useBlueprintValue) {
        const startingArray = blueprintValue as any[];

        const array: any[] = [];
        for (const startingArrayValue of startingArray) {
            const value = nestedTypeDeclaration.generateRandomValue(startingArrayValue, useBlueprintValue, ctx);

            array.push(value);
        }

        return array;
    } else {
        const length = ctx.randomGenerator.nextCollectionLength();

        const array: any[] = [];
        for (let i = 0; i < length; i++) {
            const value = nestedTypeDeclaration.generateRandomValue(null, false, ctx);

            array.push(value);
        }

        return array;
    }
}
