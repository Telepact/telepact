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
