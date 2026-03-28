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
