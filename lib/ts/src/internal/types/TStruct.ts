//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { ValidationFailure } from '../validation/ValidationFailure.js';
import { TFieldDeclaration } from './TFieldDeclaration.js';
import { TTypeDeclaration } from './TTypeDeclaration.js';
import { TType } from './TType.js';
import { validateStruct } from '../validation/ValidateStruct.js';
import { generateRandomStruct } from '../generation/GenerateRandomStruct.js';
import { GenerateContext } from '../generation/GenerateContext.js';
import { ValidateContext } from '../validation/ValidateContext.js';

export const structName: string = 'Object';

export class TStruct implements TType {
    name: string;
    fields: { [key: string]: TFieldDeclaration };

    constructor(name: string, fields: { [key: string]: TFieldDeclaration }) {
        this.name = name;
        this.fields = fields;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: TTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateStruct(value, this.name, this.fields, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: TTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomStruct(blueprintValue, useBlueprintValue, this.fields, ctx);
    }

    getName(): string {
        return structName;
    }
}
