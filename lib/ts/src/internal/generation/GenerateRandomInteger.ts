import { GenerateContext } from '../../internal/generation/GenerateContext';

export function generateRandomInteger(ctx: GenerateContext): any {
    if (ctx.useBlueprintValue) {
        return ctx.blueprintValue;
    } else {
        return ctx.randomGenerator.nextInt();
    }
}
