import { UType } from '../../internal/types/UType';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { GenerateContext } from '../../internal/generation/GenerateContext';

export function generateRandomValueOfType(
    blueprintValue: any,
    useBlueprintValue: boolean,
    thisType: UType,
    nullable: boolean,
    typeParameters: UTypeDeclaration[],
    ctx: GenerateContext,
): any {
    if (nullable && !useBlueprintValue && ctx.randomGenerator.nextBoolean()) {
        return null;
    } else {
        return thisType.generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }
}
