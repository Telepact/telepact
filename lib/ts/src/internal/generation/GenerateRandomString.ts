//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { GenerateContext } from '../../internal/generation/GenerateContext.js';

export function generateRandomString(blueprintValue: any, useBlueprintValue: boolean, ctx: GenerateContext): any {
    if (useBlueprintValue) {
        return blueprintValue;
    } else {
        return ctx.randomGenerator.nextString();
    }
}
