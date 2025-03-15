import { ValidationFailure } from '../validation/ValidationFailure';
import { VTypeDeclaration } from './VTypeDeclaration';
import { VType } from './VType';
import { validateInteger } from '../validation/ValidateInteger';
import { generateRandomInteger } from '../generation/GenerateRandomInteger';
import { GenerateContext } from '../generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const integerName: string = 'Integer';

export class VInteger extends VType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateInteger(value);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomInteger(blueprintValue, useBlueprintValue, ctx);
    }

    getName(): string {
        return integerName;
    }
}
