import { RandomGenerator } from '../../RandomGenerator';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';

export function generateRandomArray(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    typeParameters: UTypeDeclaration[],
    randomGenerator: RandomGenerator,
): any[] {
    const nestedTypeDeclaration = typeParameters[0];

    if (useBlueprintValue) {
        const startingArray = blueprintValue as any[];

        const array: any[] = [];
        for (const startingArrayValue of startingArray) {
            const value = nestedTypeDeclaration.generateRandomValue(
                startingArrayValue,
                true,
                includeOptionalFields,
                randomizeOptionalFields,
                randomGenerator,
            );

            array.push(value);
        }

        return array;
    } else {
        const length = randomGenerator.nextCollectionLength();

        const array: any[] = [];
        for (let i = 0; i < length; i++) {
            const value = nestedTypeDeclaration.generateRandomValue(
                null,
                false,
                includeOptionalFields,
                randomizeOptionalFields,
                randomGenerator,
            );

            array.push(value);
        }

        return array;
    }
}
