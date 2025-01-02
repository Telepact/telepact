import { RandomGenerator } from '../../RandomGenerator';
import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { constructRandomStruct } from '../../internal/generation/ConstructRandomStruct';

export function generateRandomStruct(
    blueprintValue: any,
    useBlueprintValue: boolean,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
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
            randomGenerator,
        );
    } else {
        return constructRandomStruct(fields, {}, includeOptionalFields, randomizeOptionalFields, randomGenerator);
    }
}
