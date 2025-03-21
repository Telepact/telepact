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
import { GenerateContext } from '../generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';
import { VTypeDeclaration } from './VTypeDeclaration';

export abstract class VType {
    abstract getTypeParameterCount(): number;

    abstract validate(value: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[];

    abstract generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any;

    abstract getName(): string;
}
