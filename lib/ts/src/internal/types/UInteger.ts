import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { UType } from '../../internal/types/UType';
import { validateInteger } from '../../internal/validation/ValidateInteger';
import { generateRandomInteger } from '../../internal/generation/GenerateRandomInteger';
import { GenerateContext } from '../../internal/generation/GenerateContext';

export const integerName: string = 'Integer';

export class UInteger extends UType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateInteger(value);
    }

    generateRandomValue(ctx: GenerateContext): any {
        return generateRandomInteger(ctx);
    }

    getName(): string {
        return integerName;
    }
}
