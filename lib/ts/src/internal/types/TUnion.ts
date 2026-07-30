//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { ValidationFailure } from '../validation/ValidationFailure.js';
import { TStruct } from './TStruct.js';
import { TTypeDeclaration } from './TTypeDeclaration.js';
import { validateUnion } from '../validation/ValidateUnion.js';
import { generateRandomUnion } from '../generation/GenerateRandomUnion.js';
import { TType } from './TType.js';
import { GenerateContext } from '../generation/GenerateContext.js';
import { ValidateContext } from '../validation/ValidateContext.js';

export const unionName: string = 'Object';

export class TUnion implements TType {
    name: string;
    tags: { [key: string]: TStruct };
    tagIndices: { [key: string]: number };

    constructor(name: string, tags: { [key: string]: TStruct }, tagIndices: { [key: string]: number }) {
        this.name = name;
        this.tags = tags;
        this.tagIndices = tagIndices;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: TTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateUnion(value, this.name, this.tags, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: TTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomUnion(blueprintValue, useBlueprintValue, this.tags, ctx);
    }

    getName(): string {
        return unionName;
    }
}
