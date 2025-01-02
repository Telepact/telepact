import { RandomGenerator } from '../../RandomGenerator';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';

export function generateRandomObject(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    typeParameters: UTypeDeclaration[],
    randomGenerator: RandomGenerator,
): any {
    const nestedTypeDeclaration = typeParameters[0];

    if (useBlueprintValue) {
        const startingObj: Record<string, any> = blueprintValue;

        const obj: Record<string, any> = {};
        for (const [key, startingObjValue] of Object.entries(startingObj)) {
            const value = nestedTypeDeclaration.generateRandomValue(
                startingObjValue,
                true,
                includeOptionalFields,
                randomizeOptionalFields,
                randomGenerator,
            );
            obj[key] = value;
        }

        return obj;
    } else {
        const length = randomGenerator.nextCollectionLength();

        const obj: Record<string, any> = {};
        for (let i = 0; i < length; i++) {
            const key = randomGenerator.nextString();
            const value = nestedTypeDeclaration.generateRandomValue(
                null,
                false,
                includeOptionalFields,
                randomizeOptionalFields,
                randomGenerator,
            );
            obj[key] = value;
        }

        return obj;
    }
}
