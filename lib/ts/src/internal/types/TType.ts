//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { ValidationFailure } from '../validation/ValidationFailure.js';
import { GenerateContext } from '../generation/GenerateContext.js';
import { ValidateContext } from '../validation/ValidateContext.js';
import { TTypeDeclaration } from './TTypeDeclaration.js';

export abstract class TType {
    abstract getTypeParameterCount(): number;

    abstract validate(value: any, typeParameters: TTypeDeclaration[], ctx: ValidateContext): ValidationFailure[];

    abstract generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: TTypeDeclaration[],
        ctx: GenerateContext,
    ): any;

    abstract getName(): string;
}
