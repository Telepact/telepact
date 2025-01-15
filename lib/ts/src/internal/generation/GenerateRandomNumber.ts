import { GenerateContext } from '../../internal/generation/GenerateContext';

export function generateRandomNumber(ctx: GenerateContext): any {
    if (ctx.useBlueprintValue) {
        return ctx.blueprintValue;
    } else {
        return ctx.randomGenerator.nextDouble();
    }
}
