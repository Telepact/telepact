//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import { TTypeDeclaration } from './TTypeDeclaration';
import { ValidationFailure } from '../validation/ValidationFailure';
import { TType } from './TType';
import { validateMockStub } from '../validation/ValidateMockStub';
import { GenerateContext } from '../generation/GenerateContext';
import { generateRandomMockStub } from '../generation/GenerateRandomMockStub';
import { ValidateContext } from '../validation/ValidateContext';

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
