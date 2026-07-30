//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { ValidationFailure } from '../validation/ValidationFailure.js';
import { TType } from './TType.js';
import { validateNumber } from '../validation/ValidateNumber.js';
import { generateRandomNumber } from '../generation/GenerateRandomNumber.js';
import { GenerateContext } from '../generation/GenerateContext.js';
import { TTypeDeclaration } from './TTypeDeclaration.js';
import { ValidateContext } from '../validation/ValidateContext.js';

export const numberName: string = 'Number';

export class TNumber extends TType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: TTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateNumber(value);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: TTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomNumber(blueprintValue, useBlueprintValue, ctx);
    }

    getName(): string {
        return numberName;
    }
}
