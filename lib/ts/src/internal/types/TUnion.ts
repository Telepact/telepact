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
