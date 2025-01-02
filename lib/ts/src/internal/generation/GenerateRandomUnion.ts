import { RandomGenerator } from '../../RandomGenerator';
import { UStruct } from '../../internal/types/UStruct';
import { constructRandomUnion } from '../../internal/generation/ConstructRandomUnion';

export function generateRandomUnion(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    randomGenerator: RandomGenerator,
    cases: { [key: string]: UStruct },
): any {
    if (useBlueprintValue) {
        const startingUnionCase = blueprintValue as { [key: string]: any };
        return constructRandomUnion(
            cases,
            startingUnionCase,
            includeOptionalFields,
            randomizeOptionalFields,
            randomGenerator,
        );
    } else {
        return constructRandomUnion(cases, {}, includeOptionalFields, randomizeOptionalFields, randomGenerator);
    }
}
