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

import { VType } from './VType';
import { ValidationFailure } from '../validation/ValidationFailure';
import { validateValueOfType } from '../validation/ValidateValueOfType';
import { generateRandomValueOfType } from '../generation/GenerateRandomValueOfType';
import { GenerateContext } from '../generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export class VTypeDeclaration {
    type: VType;
    nullable: boolean;
    typeParameters: VTypeDeclaration[];

    constructor(type: VType, nullable: boolean, typeParameters: VTypeDeclaration[]) {
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
