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

import { TType } from '../types/TType';
import { TTypeDeclaration } from '../types/TTypeDeclaration';
import { GenerateContext } from '../../internal/generation/GenerateContext';

export function generateRandomValueOfType(
    blueprintValue: any,
    useBlueprintValue: boolean,
    thisType: TType,
    nullable: boolean,
    typeParameters: TTypeDeclaration[],
    ctx: GenerateContext,
): any {
    if (nullable && !useBlueprintValue && ctx.randomGenerator.nextBoolean()) {
        return null;
    } else {
        return thisType.generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }
}
