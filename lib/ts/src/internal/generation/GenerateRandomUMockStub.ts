import { GenerateContext } from './GenerateContext';
import { UFn } from '../types/UFn';
import { UType } from '../types/UType';
import { generateRandomStruct } from './GenerateRandomStruct';

export function generateRandomUMockStub(types: { [key: string]: UType }, ctx: GenerateContext) {
    const functions: Array<UFn> = Object.entries(types)
        .filter(([key, value]) => value instanceof UFn)
        .filter(([key, value]) => !key.endsWith('_'))
        .map(([key, value]) => value as UFn);

    functions.sort((fn1, fn2) => fn1.name.localeCompare(fn2.name));

    console.log(`randomSeed: ${ctx.randomGenerator.seed}`);
    console.log(`functions: ${JSON.stringify(functions.map((fn) => fn.name))}`);

    const index = ctx.randomGenerator.nextIntWithCeiling(functions.length);

    console.log(`index: ${index}`);

    const selectedFn = functions[index];

    console.log(`selectedFn: ${selectedFn.name}`);

    const argFields = selectedFn.call.cases[selectedFn.name].fields;
    const okFields = selectedFn.result.cases['Ok_'].fields;

    const arg = generateRandomStruct(argFields, ctx.copy({ alwaysIncludeRequiredFields: false }));
    const okResult = generateRandomStruct(okFields, ctx.copy({ alwaysIncludeRequiredFields: false }));

    return {
        [selectedFn.name]: arg,
        '->': {
            Ok_: okResult,
        },
    };
}
