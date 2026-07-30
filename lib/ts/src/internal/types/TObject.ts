//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TTypeDeclaration } from './TTypeDeclaration.js';
import { ValidationFailure } from '../validation/ValidationFailure.js';
import { TType } from './TType.js';
import { validateObject } from '../validation/ValidateObject.js';
import { generateRandomObject } from '../generation/GenerateRandomObject.js';
import { GenerateContext } from '../generation/GenerateContext.js';
import { ValidateContext } from '../validation/ValidateContext.js';

export const objectName: string = 'Object';

export class TObject implements TType {
    getTypeParameterCount(): number {
        return 1;
    }

    validate(value: any, typeParameters: TTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateObject(value, typeParameters, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: TTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomObject(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }

    getName(): string {
        return objectName;
    }
}
