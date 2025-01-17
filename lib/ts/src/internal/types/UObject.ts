import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateObject } from '../../internal/validation/ValidateObject';
import { generateRandomObject } from '../../internal/generation/GenerateRandomObject';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const objectName: string = 'Object';

export class UObject implements UType {
    getTypeParameterCount(): number {
        return 1;
    }

    validate(value: any, typeParameters: UTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateObject(value, typeParameters, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: UTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomObject(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }

    getName(): string {
        return objectName;
    }
}
