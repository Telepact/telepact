import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateSelect } from '../../internal/validation/ValidateSelect';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { generateRandomSelect } from '../generation/GenerateRandomSelect';
import { ValidateContext } from '../validation/ValidateContext';

export const select: string = 'Object';

export class USelect implements UType {
    possibleSelects: Record<string, any> = {};

    getTypeParameterCount(): number {
        return 0;
    }

    validate(givenObj: any, typeParameters: UTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateSelect(givenObj, this.possibleSelects, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: UTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomSelect(this.possibleSelects, ctx);
    }

    getName(): string {
        return select;
    }
}
