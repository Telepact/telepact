import { UStruct } from '../../internal/types/UStruct';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { generateRandomStruct } from '../../internal/generation/GenerateRandomStruct';

export function generateRandomUnion(
    blueprintValue: any,
    useBlueprintValue: boolean,
    unionCasesReference: { [key: string]: UStruct },
    ctx: GenerateContext,
): any {
    if (!useBlueprintValue) {
        const sortedUnionCasesReference = Object.entries(unionCasesReference).sort((a, b) => a[0].localeCompare(b[0]));
        const randomIndex = ctx.randomGenerator.nextIntWithCeiling(sortedUnionCasesReference.length - 1);
        const [unionCase, unionData] = sortedUnionCasesReference[randomIndex];
        return {
            [unionCase]: generateRandomStruct(null, false, unionData.fields, ctx),
        };
    } else {
        const startingUnion: Record<string, any> = blueprintValue;
        const [unionCase, unionStartingStruct] = Object.entries(startingUnion)[0];
        const unionStructType = unionCasesReference[unionCase];
        return {
            [unionCase]: generateRandomStruct(unionStartingStruct, true, unionStructType.fields, ctx),
        };
    }
}
