import { UTypeDeclaration } from '../types/UTypeDeclaration';
import { GenerateContext } from './GenerateContext';

export function generateRandomObject(
    blueprintValue: any,
    useBlueprintValue: boolean,
    typeParameters: UTypeDeclaration[],
    ctx: GenerateContext,
): any {
    const nestedTypeDeclaration = typeParameters[0];

    if (useBlueprintValue) {
        const startingObj: Record<string, any> = blueprintValue;

        const obj: Record<string, any> = {};
        for (const [key, startingObjValue] of Object.entries(startingObj)) {
            const value = nestedTypeDeclaration.generateRandomValue(startingObjValue, true, ctx);
            obj[key] = value;
        }

        return obj;
    } else {
        const length = ctx.randomGenerator.nextCollectionLength();

        const obj: Record<string, any> = {};
        for (let i = 0; i < length; i++) {
            const key = ctx.randomGenerator.nextString();
            const value = nestedTypeDeclaration.generateRandomValue(null, false, ctx);
            obj[key] = value;
        }

        return obj;
    }
}
