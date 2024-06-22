import { RandomGenerator } from '../../RandomGenerator';
import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';

export function constructRandomStruct(
    referenceStruct: Record<string, UFieldDeclaration>,
    startingStruct: Record<string, any>,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    typeParameters: UTypeDeclaration[],
    randomGenerator: RandomGenerator,
): Record<string, any> {
    const sortedReferenceStruct = Object.entries(referenceStruct).sort((a, b) => a[0].localeCompare(b[0]));

    const obj: Record<string, any> = {};
    for (const [fieldName, fieldDeclaration] of sortedReferenceStruct) {
        const blueprintValue = startingStruct[fieldName];
        const useBlueprintValue = fieldName in startingStruct;
        const typeDeclaration = fieldDeclaration.typeDeclaration;

        let value: any;
        if (useBlueprintValue) {
            value = typeDeclaration.generateRandomValue(
                blueprintValue,
                useBlueprintValue,
                includeOptionalFields,
                randomizeOptionalFields,
                typeParameters,
                randomGenerator,
            );
        } else {
            if (!fieldDeclaration.optional) {
                value = typeDeclaration.generateRandomValue(
                    null,
                    false,
                    includeOptionalFields,
                    randomizeOptionalFields,
                    typeParameters,
                    randomGenerator,
                );
            } else {
                if (!includeOptionalFields || (randomizeOptionalFields && randomGenerator.nextBoolean())) {
                    continue;
                }
                value = typeDeclaration.generateRandomValue(
                    null,
                    false,
                    includeOptionalFields,
                    randomizeOptionalFields,
                    typeParameters,
                    randomGenerator,
                );
            }
        }

        obj[fieldName] = value;
    }

    return obj;
}
