import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateNumber } from '../../internal/validation/ValidateNumber';
import { generateRandomNumber } from '../../internal/generation/GenerateRandomNumber';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidateContext } from '../validation/ValidateContext';

export const numberName: string = 'Number';

export class UNumber extends UType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: UTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateNumber(value);
    }

    generateRandomValue(ctx: GenerateContext): any {
        return generateRandomNumber(ctx);
    }

    getName(): string {
        return numberName;
    }
}
