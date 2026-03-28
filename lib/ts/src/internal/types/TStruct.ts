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
