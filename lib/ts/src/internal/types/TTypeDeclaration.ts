//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TType } from './TType.js';
import { ValidationFailure } from '../validation/ValidationFailure.js';
import { validateValueOfType } from '../validation/ValidateValueOfType.js';
import { generateRandomValueOfType } from '../generation/GenerateRandomValueOfType.js';
import { GenerateContext } from '../generation/GenerateContext.js';
import { ValidateContext } from '../validation/ValidateContext.js';

export class TTypeDeclaration {
    type: TType;
    nullable: boolean;
    typeParameters: TTypeDeclaration[];

    constructor(type: TType, nullable: boolean, typeParameters: TTypeDeclaration[]) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }

    validate(value: any, ctx: ValidateContext): ValidationFailure[] {
        return validateValueOfType(value, this.type, this.nullable, this.typeParameters, ctx);
    }

    generateRandomValue(blueprintValue: any, useBlueprintValue: boolean, ctx: GenerateContext): any {
        return generateRandomValueOfType(
            blueprintValue,
            useBlueprintValue,
            this.type,
            this.nullable,
            this.typeParameters,
            ctx,
        );
    }
}
