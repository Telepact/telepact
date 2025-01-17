import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { UType } from '../../internal/types/UType';
import { validateInteger } from '../../internal/validation/ValidateInteger';
import { generateRandomInteger } from '../../internal/generation/GenerateRandomInteger';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const integerName: string = 'Integer';

export class UInteger extends UType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: UTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateInteger(value);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: UTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomInteger(blueprintValue, useBlueprintValue, ctx);
    }

    getName(): string {
        return integerName;
    }
}
