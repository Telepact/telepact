import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { UType } from '../../internal/types/UType';
import { validateBoolean } from '../../internal/validation/ValidateBoolean';
import { generateRandomBoolean } from '../../internal/generation/GenerateRandomBoolean';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const booleanName: string = 'Boolean';

export class UBoolean extends UType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: UTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateBoolean(value);
    }

    generateRandomValue(ctx: GenerateContext): any {
        return generateRandomBoolean(ctx);
    }

    getName(): string {
        return booleanName;
    }
}
