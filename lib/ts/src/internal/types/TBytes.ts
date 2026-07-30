//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { ValidationFailure } from '../validation/ValidationFailure.js';
import { TTypeDeclaration } from './TTypeDeclaration.js';
import { TType } from './TType.js';
import { validateBytes } from '../validation/ValidateBytes.js';
import { generateRandomBytes } from '../generation/GenerateRandomBytes.js';
import { GenerateContext } from '../generation/GenerateContext.js';
import { ValidateContext } from '../validation/ValidateContext.js';

export const bytesName: string = 'Bytes';

export class TBytes extends TType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: TTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateBytes(value, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: TTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomBytes(blueprintValue, useBlueprintValue, ctx);
    }

    getName(): string {
        return bytesName;
    }
}
