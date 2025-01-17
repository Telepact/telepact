import { GenerateContext } from '../../internal/generation/GenerateContext';
import { UTypeDeclaration } from '../types/UTypeDeclaration';

export function generateRandomArray(
    blueprintValue: any,
    useBlueprintValue: boolean,
    typeParameters: UTypeDeclaration[],
    ctx: GenerateContext,
): any[] {
    const nestedTypeDeclaration = typeParameters[0];

    if (useBlueprintValue) {
        const startingArray = blueprintValue as any[];

        const array: any[] = [];
        for (const startingArrayValue of startingArray) {
            const value = nestedTypeDeclaration.generateRandomValue(startingArrayValue, useBlueprintValue, ctx);

            array.push(value);
        }

        return array;
    } else {
        const length = ctx.randomGenerator.nextCollectionLength();

        const array: any[] = [];
        for (let i = 0; i < length; i++) {
            const value = nestedTypeDeclaration.generateRandomValue(null, false, ctx);

            array.push(value);
        }

        return array;
    }
}
