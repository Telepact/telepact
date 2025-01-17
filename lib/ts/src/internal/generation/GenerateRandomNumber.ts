import { GenerateContext } from '../../internal/generation/GenerateContext';

export function generateRandomNumber(blueprintValue: any, useBlueprintValue: boolean, ctx: GenerateContext): any {
    if (useBlueprintValue) {
        return blueprintValue;
    } else {
        return ctx.randomGenerator.nextDouble();
    }
}
