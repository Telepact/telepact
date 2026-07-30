//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TTypeDeclaration } from './TTypeDeclaration.js';
import { ValidationFailure } from '../validation/ValidationFailure.js';
import { TType } from './TType.js';
import { validateMockCall } from '../validation/ValidateMockCall.js';
import { GenerateContext } from '../generation/GenerateContext.js';
import { generateRandomMockCall } from '../generation/GenerateRandomMockCall.js';
import { ValidateContext } from '../validation/ValidateContext.js';

export const mockCallName: string = '_ext.Call_';

export class TMockCall extends TType {
    private types: { [key: string]: TType };

    constructor(types: { [key: string]: TType }) {
        super();
        this.types = types;
    }

    public getTypeParameterCount(): number {
        return 0;
    }

    public validate(givenObj: any, typeParameters: TTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateMockCall(givenObj, this.types, ctx);
    }

    public generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: TTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomMockCall(this.types, ctx);
    }

    public getName(): string {
        return mockCallName;
    }
}
