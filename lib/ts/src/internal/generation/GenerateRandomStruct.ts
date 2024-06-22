import { RandomGenerator } from '../../RandomGenerator';
import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { constructRandomStruct } from '../../internal/generation/ConstructRandomStruct';

export function generateRandomStruct(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    typeParameters: UTypeDeclaration[],
    generics: UTypeDeclaration[],
    randomGenerator: RandomGenerator,
    fields: { [key: string]: UFieldDeclaration },
): any {
    if (useBlueprintValue) {
        // Assuming blueprintValue is already a dictionary
        const startingStructValue = blueprintValue as { [key: string]: any };
        return constructRandomStruct(
            fields,
            startingStructValue,
            includeOptionalFields,
            randomizeOptionalFields,
            typeParameters,
            randomGenerator,
        );
    } else {
        return constructRandomStruct(
            fields,
            {},
            includeOptionalFields,
            randomizeOptionalFields,
            typeParameters,
            randomGenerator,
        );
    }
}
