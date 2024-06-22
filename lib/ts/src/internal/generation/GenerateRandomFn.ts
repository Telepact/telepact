import { RandomGenerator } from '../../RandomGenerator';
import { UStruct } from '../../internal/types/UStruct';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { constructRandomUnion } from '../../internal/generation/ConstructRandomUnion';

export function generateRandomFn(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    typeParameters: UTypeDeclaration[],
    generics: UTypeDeclaration[],
    randomGenerator: RandomGenerator,
    callCases: { [key: string]: UStruct },
): any {
    if (useBlueprintValue) {
        // Assuming blueprintValue is already a dictionary
        const startingFnValue: { [key: string]: any } = blueprintValue;
        return constructRandomUnion(
            callCases,
            startingFnValue,
            includeOptionalFields,
            randomizeOptionalFields,
            [],
            randomGenerator,
        );
    } else {
        return constructRandomUnion(callCases, {}, includeOptionalFields, randomizeOptionalFields, [], randomGenerator);
    }
}
