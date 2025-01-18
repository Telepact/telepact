import { GenerateContext } from './GenerateContext';
import { generateRandomUnion } from './GenerateRandomUnion';
import { UFn } from '../types/UFn';
import { UType } from '../types/UType';

export function generateRandomUMockCall(types: { [key: string]: UType }, ctx: GenerateContext) {
    const functions: Array<UFn> = Object.entries(types)
        .filter(([key, value]) => value instanceof UFn)
        .filter(([key, value]) => !key.endsWith('_'))
        .map(([key, value]) => value as UFn);

    functions.sort((fn1, fn2) => fn1.name.localeCompare(fn2.name));

    const selectedFn = functions[Math.floor(ctx.randomGenerator.nextIntWithCeiling(functions.length))];

    return generateRandomUnion(null, false, selectedFn.call.cases, ctx.copy({ alwaysIncludeRequiredFields: false }));
}
