import { RandomGenerator } from 'uapi/RandomGenerator';
import { UStruct } from 'uapi/internal/types/UStruct';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { constructRandomUnion } from 'uapi/internal/generation/ConstructRandomUnion';

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
