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
import { TType } from '../types/TType';
import { generateRandomStruct } from './GenerateRandomStruct';
import { TUnion } from '../types/TUnion';

export function generateRandomMockStub(types: { [key: string]: TType }, ctx: GenerateContext): object {
    const functions: string[] = Object.keys(types)
        .filter((key) => key.startsWith('fn.') && !key.endsWith('.->'))
        .filter((key) => !key.endsWith('_'))
        .map((key) => key);

    functions.sort((fn1, fn2) => fn1.localeCompare(fn2));

    const index = ctx.randomGenerator.nextIntWithCeiling(functions.length);

    const selectedFn = functions[index];

    const selectedArgs = types[selectedFn] as TUnion;
    const selectedResult = types[selectedFn + '.->'] as TUnion;

    const argFields = selectedArgs.tags[selectedFn].fields;
    const okFields = selectedResult.tags['Ok_'].fields;

    const arg = generateRandomStruct(null, false, argFields, ctx.copy({ alwaysIncludeRequiredFields: false }));
    const okResult = generateRandomStruct(null, false, okFields, ctx.copy({ alwaysIncludeRequiredFields: false }));

    return {
        [selectedFn]: arg,
        '->': {
            Ok_: okResult,
        },
    };
}
