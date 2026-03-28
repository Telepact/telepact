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

import { TTypeDeclaration } from '../types/TTypeDeclaration';
import { GenerateContext } from './GenerateContext';

export function generateRandomObject(
    blueprintValue: any,
    useBlueprintValue: boolean,
    typeParameters: TTypeDeclaration[],
    ctx: GenerateContext,
): any {
    const nestedTypeDeclaration = typeParameters[0];

    if (useBlueprintValue) {
        const startingObj: Record<string, any> = blueprintValue;

        const obj: Record<string, any> = {};
        for (const [key, startingObjValue] of Object.entries(startingObj)) {
            const value = nestedTypeDeclaration.generateRandomValue(startingObjValue, true, ctx);
            obj[key] = value;
        }

        return obj;
    } else {
        const length = ctx.randomGenerator.nextCollectionLength();

        const obj: Record<string, any> = {};
        for (let i = 0; i < length; i++) {
            const key = ctx.randomGenerator.nextString();
            const value = nestedTypeDeclaration.generateRandomValue(null, false, ctx);
            obj[key] = value;
        }

        return obj;
    }
}
