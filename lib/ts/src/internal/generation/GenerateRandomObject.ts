import { GenerateContext } from './GenerateContext';

export function generateRandomObject(ctx: GenerateContext): any {
    const nestedTypeDeclaration = ctx.typeParameters[0];

    if (ctx.useBlueprintValue) {
        const startingObj: Record<string, any> = ctx.blueprintValue;

        const obj: Record<string, any> = {};
        for (const [key, startingObjValue] of Object.entries(startingObj)) {
            const value = nestedTypeDeclaration.generateRandomValue(ctx.copy({ blueprintValue: startingObjValue }));
            obj[key] = value;
        }

        return obj;
    } else {
        const length = ctx.randomGenerator.nextCollectionLength();

        const obj: Record<string, any> = {};
        for (let i = 0; i < length; i++) {
            const key = ctx.randomGenerator.nextString();
            const value = nestedTypeDeclaration.generateRandomValue(ctx);
            obj[key] = value;
        }

        return obj;
    }
}
