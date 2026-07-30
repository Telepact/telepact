//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { ValidationFailure } from '../validation/ValidationFailure.js';
import { TTypeDeclaration } from './TTypeDeclaration.js';
import { TType } from './TType.js';
import { validateArray } from '../validation/ValidateArray.js';
import { generateRandomArray } from '../generation/GenerateRandomArray.js';
import { GenerateContext } from '../generation/GenerateContext.js';
import { ValidateContext } from '../validation/ValidateContext.js';

export const arrayName = 'Array';

export class TArray extends TType {
    getTypeParameterCount(): number {
        return 1;
    }

    validate(value: any, typeParameters: TTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateArray(value, typeParameters, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: TTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomArray(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }

    getName(): string {
        return arrayName;
    }
}
