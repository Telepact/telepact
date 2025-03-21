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

import { ValidationFailure } from '../validation/ValidationFailure';
import { VTypeDeclaration } from './VTypeDeclaration';
import { VType } from './VType';
import { validateBoolean } from '../validation/ValidateBoolean';
import { generateRandomBoolean } from '../generation/GenerateRandomBoolean';
import { GenerateContext } from '../generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const booleanName: string = 'Boolean';

export class VBoolean extends VType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateBoolean(value);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomBoolean(blueprintValue, useBlueprintValue, ctx);
    }

    getName(): string {
        return booleanName;
    }
}
