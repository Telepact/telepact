import { GenerateContext } from './GenerateContext';
import { VFn } from '../types/VFn';
import { VType } from '../types/VType';
import { generateRandomStruct } from './GenerateRandomStruct';

export function generateRandomUMockStub(types: { [key: string]: VType }, ctx: GenerateContext): object {
    const functions: Array<VFn> = Object.entries(types)
        .filter(([key, value]) => value instanceof VFn)
        .filter(([key, value]) => !key.endsWith('_'))
        .map(([key, value]) => value as VFn);

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
