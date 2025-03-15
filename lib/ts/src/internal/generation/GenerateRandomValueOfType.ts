import { VType } from '../types/VType';
import { VTypeDeclaration } from '../types/VTypeDeclaration';
import { GenerateContext } from '../../internal/generation/GenerateContext';

export function generateRandomValueOfType(
    blueprintValue: any,
    useBlueprintValue: boolean,
    thisType: VType,
    nullable: boolean,
    typeParameters: VTypeDeclaration[],
    ctx: GenerateContext,
): any {
    if (nullable && !useBlueprintValue && ctx.randomGenerator.nextBoolean()) {
        return null;
    } else {
        return thisType.generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }
}
