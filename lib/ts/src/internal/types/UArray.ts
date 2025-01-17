import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { UType } from '../../internal/types/UType';
import { validateArray } from '../../internal/validation/ValidateArray';
import { generateRandomArray } from '../../internal/generation/GenerateRandomArray';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const arrayName = 'Array';

export class UArray extends UType {
    getTypeParameterCount(): number {
        return 1;
    }

    validate(value: any, typeParameters: UTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateArray(value, typeParameters, ctx);
    }

    generateRandomValue(ctx: GenerateContext): any {
        return generateRandomArray(ctx);
    }

    getName(): string {
        return arrayName;
    }
}
