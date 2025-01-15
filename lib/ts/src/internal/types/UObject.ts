import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateObject } from '../../internal/validation/ValidateObject';
import { generateRandomObject } from '../../internal/generation/GenerateRandomObject';
import { GenerateContext } from '../../internal/generation/GenerateContext';

export const objectName: string = 'Object';

export class UObject implements UType {
    getTypeParameterCount(): number {
        return 1;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateObject(value, select, fn, typeParameters);
    }

    generateRandomValue(ctx: GenerateContext): any {
        return generateRandomObject(ctx);
    }

    getName(): string {
        return objectName;
    }
}
