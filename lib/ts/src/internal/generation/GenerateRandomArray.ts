import { GenerateContext } from '../../internal/generation/GenerateContext';

export function generateRandomArray(ctx: GenerateContext): any[] {
    const nestedTypeDeclaration = ctx.typeParameters[0];

    if (ctx.useBlueprintValue) {
        const startingArray = ctx.blueprintValue as any[];

        const array: any[] = [];
        for (const startingArrayValue of startingArray) {
            const value = nestedTypeDeclaration.generateRandomValue(ctx.copy({ blueprintValue: startingArrayValue }));

            array.push(value);
        }

        return array;
    } else {
        const length = ctx.randomGenerator.nextCollectionLength();

        const array: any[] = [];
        for (let i = 0; i < length; i++) {
            const value = nestedTypeDeclaration.generateRandomValue(ctx);

            array.push(value);
        }

        return array;
    }
}
