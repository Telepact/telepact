import { RandomGenerator } from 'uapi/RandomGenerator';
import { UType } from 'uapi/internal/types/UType';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';

export function generateRandomValueOfType(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    generics: UTypeDeclaration[],
    randomGenerator: RandomGenerator,
    thisType: UType,
    nullable: boolean,
    typeParameters: UTypeDeclaration[],
): any {
    if (nullable && !useBlueprintValue && randomGenerator.nextBoolean()) {
        return null;
    } else {
        return thisType.generateRandomValue(
            blueprintValue,
            useBlueprintValue,
            includeOptionalFields,
            randomizeOptionalFields,
            typeParameters,
            generics,
            randomGenerator,
        );
    }
}
