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
    const sortedReferenceStruct = Array.from(Object.entries(referenceStruct)).sort((e1, e2) => {
        const a = e1[0];
        const b = e2[0];
        for (let i = 0; i < Math.min(a.length, b.length); i++) {
            const charCodeA = a.charCodeAt(i);
            const charCodeB = b.charCodeAt(i);
            if (charCodeA !== charCodeB) {
                // If the characters are different, return the comparison result
                // where lowercase letters are considered greater than uppercase letters
                return charCodeA - charCodeB;
            }
        }
        // If one string is a prefix of the other, the shorter string comes first
        return a.length - b.length;
    });

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
