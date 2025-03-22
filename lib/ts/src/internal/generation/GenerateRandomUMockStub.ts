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
import { TFn } from '../types/TFn';
import { TType } from '../types/TType';
import { generateRandomStruct } from './GenerateRandomStruct';

export function generateRandomUMockStub(types: { [key: string]: TType }, ctx: GenerateContext): object {
    const functions: Array<TFn> = Object.entries(types)
        .filter(([key, value]) => value instanceof TFn)
        .filter(([key, value]) => !key.endsWith('_'))
        .map(([key, value]) => value as TFn);

    functions.sort((fn1, fn2) => fn1.name.localeCompare(fn2.name));

    console.log(`randomSeed: ${ctx.randomGenerator.seed}`);
    console.log(`functions: ${JSON.stringify(functions.map((fn) => fn.name))}`);

    const index = ctx.randomGenerator.nextIntWithCeiling(functions.length);

    console.log(`index: ${index}`);

    const selectedFn = functions[index];

    console.log(`selectedFn: ${selectedFn.name}`);

    const argFields = selectedFn.call.tags[selectedFn.name].fields;
    const okFields = selectedFn.result.tags['Ok_'].fields;

    const arg = generateRandomStruct(null, false, argFields, ctx.copy({ alwaysIncludeRequiredFields: false }));
    const okResult = generateRandomStruct(null, false, okFields, ctx.copy({ alwaysIncludeRequiredFields: false }));

    return {
        [selectedFn.name]: arg,
        '->': {
            Ok_: okResult,
        },
    };
}
