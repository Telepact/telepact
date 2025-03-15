import { GenerateContext } from './GenerateContext';
import { generateRandomUnion } from './GenerateRandomUnion';
import { VFn } from '../types/VFn';
import { VType } from '../types/VType';

export function generateRandomUMockCall(types: { [key: string]: VType }, ctx: GenerateContext) {
    const functions: Array<VFn> = Object.entries(types)
        .filter(([key, value]) => value instanceof VFn)
        .filter(([key, value]) => !key.endsWith('_'))
        .map(([key, value]) => value as VFn);

    functions.sort((fn1, fn2) => fn1.name.localeCompare(fn2.name));

    const selectedFn = functions[Math.floor(ctx.randomGenerator.nextIntWithCeiling(functions.length))];

    return generateRandomUnion(null, false, selectedFn.call.tags, ctx.copy({ alwaysIncludeRequiredFields: false }));
}
