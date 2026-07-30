//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { ValidationFailure } from '../validation/ValidationFailure.js';
import { TTypeDeclaration } from './TTypeDeclaration.js';
import { TType } from './TType.js';
import { validateBoolean } from '../validation/ValidateBoolean.js';
import { generateRandomBoolean } from '../generation/GenerateRandomBoolean.js';
import { GenerateContext } from '../generation/GenerateContext.js';
import { ValidateContext } from '../validation/ValidateContext.js';

export const booleanName: string = 'Boolean';

export class TBoolean extends TType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: TTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateBoolean(value);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: TTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomBoolean(blueprintValue, useBlueprintValue, ctx);
    }

    getName(): string {
        return booleanName;
    }
}
