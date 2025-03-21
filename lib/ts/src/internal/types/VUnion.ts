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
import { VStruct } from './VStruct';
import { VTypeDeclaration } from './VTypeDeclaration';
import { validateUnion } from '../validation/ValidateUnion';
import { generateRandomUnion } from '../generation/GenerateRandomUnion';
import { VType } from './VType';
import { GenerateContext } from '../generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const unionName: string = 'Object';

export class VUnion implements VType {
    name: string;
    tags: { [key: string]: VStruct };
    tagIndices: { [key: string]: number };

    constructor(name: string, tags: { [key: string]: VStruct }, tagIndices: { [key: string]: number }) {
        this.name = name;
        this.tags = tags;
        this.tagIndices = tagIndices;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateUnion(value, this.name, this.tags, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomUnion(blueprintValue, useBlueprintValue, this.tags, ctx);
    }

    getName(): string {
        return unionName;
    }
}
