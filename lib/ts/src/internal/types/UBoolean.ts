import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { UType } from '../../internal/types/UType';
import { validateBoolean } from '../../internal/validation/ValidateBoolean';
import { generateRandomBoolean } from '../../internal/generation/GenerateRandomBoolean';
import { GenerateContext } from '../../internal/generation/GenerateContext';

export const booleanName: string = 'Boolean';

export class UBoolean extends UType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateBoolean(value);
    }

    generateRandomValue(ctx: GenerateContext): any {
        return generateRandomBoolean(ctx);
    }

    getName(): string {
        return booleanName;
    }
}
