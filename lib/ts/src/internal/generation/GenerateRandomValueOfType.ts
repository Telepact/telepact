import { RandomGenerator } from '../../RandomGenerator';
import { UType } from '../../internal/types/UType';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';

export function generateRandomValueOfType(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
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
            randomGenerator,
        );
    }
}
