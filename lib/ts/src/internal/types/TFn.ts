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
import { TUnion } from './TUnion';
import { ValidationFailure } from '../validation/ValidationFailure';
import { TType } from './TType';
import { GenerateContext } from '../generation/GenerateContext';
import { generateRandomUnion } from '../generation/GenerateRandomUnion';
import { ValidateContext } from '../validation/ValidateContext';

const FN_NAME = 'Object';

export class TFn extends TType {
    name: string;
    call: TUnion;
    result: TUnion;
    errorsRegex: string;
    inheritedErrors: string[] = [];

    constructor(name: string, call: TUnion, output: TUnion, errorsRegex: string) {
        super();
        this.name = name;
        this.call = call;
        this.result = output;
        this.errorsRegex = errorsRegex;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: TTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return this.call.validate(value, [], ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: TTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomUnion(blueprintValue, useBlueprintValue, this.call.tags, ctx);
    }

    getName(): string {
        return FN_NAME;
    }
}
