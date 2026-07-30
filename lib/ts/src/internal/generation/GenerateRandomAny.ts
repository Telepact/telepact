//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { GenerateContext } from '../../internal/generation/GenerateContext.js';

export function generateRandomAny(ctx: GenerateContext): any {
    const selectType = ctx.randomGenerator.nextIntWithCeiling(3);
    if (selectType === 0) {
        return ctx.randomGenerator.nextBoolean();
    } else if (selectType === 1) {
        return ctx.randomGenerator.nextInt();
    } else {
        return ctx.randomGenerator.nextString();
    }
}
