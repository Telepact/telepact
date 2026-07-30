//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { GenerateContext } from '../../internal/generation/GenerateContext.js';
import { TTypeDeclaration } from '../types/TTypeDeclaration.js';

export function generateRandomArray(
    blueprintValue: any,
    useBlueprintValue: boolean,
    typeParameters: TTypeDeclaration[],
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
