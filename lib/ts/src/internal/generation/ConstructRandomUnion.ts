import { RandomGenerator } from '../../RandomGenerator';
import { UStruct } from '../../internal/types/UStruct';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { constructRandomStruct } from '../../internal/generation/ConstructRandomStruct';

export function constructRandomUnion(
    unionCasesReference: Record<string, UStruct>,
    startingUnion: Record<string, any>,
    includeOptionalFields: boolean,
    randomizeOptionalFields: boolean,
    typeParameters: UTypeDeclaration[],
    randomGenerator: RandomGenerator,
): Record<string, any> {
    if (Object.keys(startingUnion).length === 0) {
        const sortedUnionCasesReference = Object.entries(unionCasesReference).sort((a, b) => a[0].localeCompare(b[0]));
        const randomIndex = randomGenerator.nextIntWithCeiling(sortedUnionCasesReference.length - 1);
        const [unionCase, unionData] = sortedUnionCasesReference[randomIndex];
        return {
            [unionCase]: constructRandomStruct(
                unionData.fields,
                {},
                includeOptionalFields,
                randomizeOptionalFields,
                typeParameters,
                randomGenerator,
            ),
        };
    } else {
        const [unionCase, unionStartingStruct] = Object.entries(startingUnion)[0];
        const unionStructType = unionCasesReference[unionCase];
        return {
            [unionCase]: constructRandomStruct(
                unionStructType.fields,
                unionStartingStruct,
                includeOptionalFields,
                randomizeOptionalFields,
                typeParameters,
                randomGenerator,
            ),
        };
    }
}
