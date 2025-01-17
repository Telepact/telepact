import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { generateRandomAny } from '../../internal/generation/GenerateRandomAny';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

const anyName = 'Any';

export class UAny extends UType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: UTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return [];
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: UTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomAny(ctx);
    }

    getName(): string {
        return anyName;
    }
}
