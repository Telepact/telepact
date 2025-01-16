import { UType } from '../../internal/types/UType';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { GenerateContext } from '../../internal/generation/GenerateContext';

export function generateRandomValueOfType(
    thisType: UType,
    nullable: boolean,
    typeParameters: UTypeDeclaration[],
    ctx: GenerateContext,
): any {
    if (nullable && !ctx.useBlueprintValue && ctx.randomGenerator.nextBoolean()) {
        return null;
    } else {
        return thisType.generateRandomValue(ctx.copy({ typeParameters }));
    }
}
