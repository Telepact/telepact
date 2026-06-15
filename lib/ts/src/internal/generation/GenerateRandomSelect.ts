//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { GenerateContext } from './GenerateContext.js';

export function generateRandomSelect(possibleSelects: Record<string, any>, ctx: GenerateContext): object {
    const possibleSelect = possibleSelects[ctx.fnScope];
    return subSelect(possibleSelect, ctx);
}

function subSelect(possibleSelectSection: any, ctx: GenerateContext): any {
    if (Array.isArray(possibleSelectSection)) {
        const selectedFieldNames = [];

        for (const fieldName of possibleSelectSection) {
            if (ctx.randomGenerator.nextBoolean()) {
                selectedFieldNames.push(fieldName);
            }
        }

        return selectedFieldNames.sort();
    } else if (typeof possibleSelectSection === 'object' && !Array.isArray(possibleSelectSection)) {
        const selectedSection: Record<string, any> = {};

        const keys = Object.keys(possibleSelectSection).sort();

        for (const key of keys) {
            const value = possibleSelectSection[key];
            if (ctx.randomGenerator.nextBoolean()) {
                const result = subSelect(value, ctx);
                if (typeof result === 'object' && !Array.isArray(result) && Object.keys(result).length === 0) {
                    continue;
                }
                selectedSection[key] = result;
            }
        }

        return selectedSection;
    } else {
        throw new Error('Invalid possibleSelectSection');
    }
}
