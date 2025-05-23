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

import { GenerateContext } from './GenerateContext';
import { generateRandomUnion } from './GenerateRandomUnion';
import { TType } from '../types/TType';
import { TUnion } from '../types/TUnion';

export function generateRandomUMockCall(types: { [key: string]: TType }, ctx: GenerateContext) {
    const functions: Array<TUnion> = Object.entries(types)
        .filter(([key, value]) => key.startsWith('fn.') && !key.endsWith('.->'))
        .filter(([key, value]) => !key.endsWith('_'))
        .map(([key, value]) => value as TUnion);

    functions.sort((fn1, fn2) => fn1.name.localeCompare(fn2.name));

    const selectedFn = functions[Math.floor(ctx.randomGenerator.nextIntWithCeiling(functions.length))];

    return generateRandomUnion(null, false, selectedFn.tags, ctx.copy({ alwaysIncludeRequiredFields: false }));
}
