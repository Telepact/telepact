//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { GenerateContext } from './GenerateContext.js';
import { generateRandomUnion } from './GenerateRandomUnion.js';
import { TType } from '../types/TType.js';
import { TUnion } from '../types/TUnion.js';

export function generateRandomMockCall(types: { [key: string]: TType }, ctx: GenerateContext) {
    const functions: Array<TUnion> = Object.entries(types)
        .filter(([key, value]) => key.startsWith('fn.') && !key.endsWith('.->'))
        .filter(([key, value]) => !key.endsWith('_'))
        .map(([key, value]) => value as TUnion);

    functions.sort((fn1, fn2) => fn1.name.localeCompare(fn2.name));

    const selectedFn = functions[Math.floor(ctx.randomGenerator.nextIntWithCeiling(functions.length))];

    return generateRandomUnion(null, false, selectedFn.tags, ctx.copy({ alwaysIncludeRequiredFields: false }));
}
