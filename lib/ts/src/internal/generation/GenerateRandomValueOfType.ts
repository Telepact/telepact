//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TType } from '../types/TType.js';
import { TTypeDeclaration } from '../types/TTypeDeclaration.js';
import { GenerateContext } from '../../internal/generation/GenerateContext.js';

export function generateRandomValueOfType(
    blueprintValue: any,
    useBlueprintValue: boolean,
    thisType: TType,
    nullable: boolean,
    typeParameters: TTypeDeclaration[],
    ctx: GenerateContext,
): any {
    if (nullable && !useBlueprintValue && ctx.randomGenerator.nextBoolean()) {
        return null;
    } else {
        return thisType.generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }
}
