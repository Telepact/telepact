import { GenerateContext } from '../../internal/generation/GenerateContext';

export function generateRandomBoolean(ctx: GenerateContext): any {
    if (ctx.useBlueprintValue) {
        return ctx.blueprintValue;
    } else {
        return ctx.randomGenerator.nextBoolean();
    }
}
