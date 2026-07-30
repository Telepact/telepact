//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TTypeDeclaration } from './TTypeDeclaration.js';
import { ValidationFailure } from '../validation/ValidationFailure.js';
import { TType } from './TType.js';
import { validateMockStub } from '../validation/ValidateMockStub.js';
import { GenerateContext } from '../generation/GenerateContext.js';
import { generateRandomMockStub } from '../generation/GenerateRandomMockStub.js';
import { ValidateContext } from '../validation/ValidateContext.js';

export const mockStubName: string = '_ext.Stub_';

export class TMockStub extends TType {
    types: { [key: string]: TType };

    constructor(types: { [key: string]: TType }) {
        super();
        this.types = types;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(givenObj: any, typeParameters: TTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateMockStub(givenObj, this.types, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: TTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomMockStub(this.types, ctx);
    }

    getName(): string {
        return mockStubName;
    }
}
