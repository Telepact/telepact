//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TTypeDeclaration } from './TTypeDeclaration.js';
import { ValidationFailure } from '../validation/ValidationFailure.js';
import { TType } from './TType.js';
import { validateSelect } from '../validation/ValidateSelect.js';
import { GenerateContext } from '../generation/GenerateContext.js';
import { generateRandomSelect } from '../generation/GenerateRandomSelect.js';
import { ValidateContext } from '../validation/ValidateContext.js';

export const select: string = 'Object';

export class TSelect implements TType {
    possibleSelects: Record<string, any> = {};

    getTypeParameterCount(): number {
        return 0;
    }

    validate(givenObj: any, typeParameters: TTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateSelect(givenObj, this.possibleSelects, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: TTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomSelect(this.possibleSelects, ctx);
    }

    getName(): string {
        return select;
    }
}
