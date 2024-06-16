import { RandomGenerator } from 'uapi/RandomGenerator';
import { UStruct } from 'uapi/internal/types/UStruct';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { constructRandomUnion } from 'uapi/internal/generation/ConstructRandomUnion';

export function generateRandomUnion(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    typeParameters: UTypeDeclaration[],
    generics: UTypeDeclaration[],
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
            typeParameters,
            randomGenerator,
        );
    } else {
        return constructRandomUnion(
            cases,
            {},
            includeOptionalFields,
            randomizeOptionalFields,
            typeParameters,
            randomGenerator,
        );
    }
}
