//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TTypeDeclaration } from './TTypeDeclaration.js';
import { ValidationFailure } from '../validation/ValidationFailure.js';
import { TType } from './TType.js';
import { validateString } from '../validation/ValidateString.js';
import { generateRandomString } from '../generation/GenerateRandomString.js';
import { GenerateContext } from '../generation/GenerateContext.js';
import { ValidateContext } from '../validation/ValidateContext.js';

export const stringName: string = 'String';

export class TString extends TType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: TTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateString(value);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: TTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomString(blueprintValue, useBlueprintValue, ctx);
    }

    getName(): string {
        return stringName;
    }
}
