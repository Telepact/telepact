import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateString } from '../../internal/validation/ValidateString';
import { generateRandomString } from '../../internal/generation/GenerateRandomString';
import { GenerateContext } from '../../internal/generation/GenerateContext';

export const stringName: string = 'String';

export class UString extends UType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateString(value);
    }

    generateRandomValue(ctx: GenerateContext): any {
        return generateRandomString(ctx);
    }

    getName(): string {
        return stringName;
    }
}
