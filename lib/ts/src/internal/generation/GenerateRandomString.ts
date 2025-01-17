import { GenerateContext } from '../../internal/generation/GenerateContext';

export function generateRandomString(blueprintValue: any, useBlueprintValue: boolean, ctx: GenerateContext): any {
    if (useBlueprintValue) {
        return blueprintValue;
    } else {
        return ctx.randomGenerator.nextString();
    }
}
