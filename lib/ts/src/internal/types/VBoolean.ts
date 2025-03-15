import { ValidationFailure } from '../validation/ValidationFailure';
import { VTypeDeclaration } from './VTypeDeclaration';
import { VType } from './VType';
import { validateBoolean } from '../validation/ValidateBoolean';
import { generateRandomBoolean } from '../generation/GenerateRandomBoolean';
import { GenerateContext } from '../generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const booleanName: string = 'Boolean';

export class VBoolean extends VType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateBoolean(value);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomBoolean(blueprintValue, useBlueprintValue, ctx);
    }

    getName(): string {
        return booleanName;
    }
}
