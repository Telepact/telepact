//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { ValidationFailure } from '../validation/ValidationFailure.js';
import { TTypeDeclaration } from './TTypeDeclaration.js';
import { TType } from './TType.js';
import { validateInteger } from '../validation/ValidateInteger.js';
import { generateRandomInteger } from '../generation/GenerateRandomInteger.js';
import { GenerateContext } from '../generation/GenerateContext.js';
import { ValidateContext } from '../validation/ValidateContext.js';

export const integerName: string = 'Integer';

export class TInteger extends TType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: TTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateInteger(value);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: TTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomInteger(blueprintValue, useBlueprintValue, ctx);
    }

    getName(): string {
        return integerName;
    }
}
