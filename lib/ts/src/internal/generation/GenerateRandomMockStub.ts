//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { GenerateContext } from './GenerateContext.js';
import { TType } from '../types/TType.js';
import { generateRandomStruct } from './GenerateRandomStruct.js';
import { TUnion } from '../types/TUnion.js';

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
