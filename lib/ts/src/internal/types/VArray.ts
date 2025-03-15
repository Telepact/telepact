import { ValidationFailure } from '../validation/ValidationFailure';
import { VTypeDeclaration } from './VTypeDeclaration';
import { VType } from './VType';
import { validateArray } from '../validation/ValidateArray';
import { generateRandomArray } from '../generation/GenerateRandomArray';
import { GenerateContext } from '../generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const arrayName = 'Array';

export class VArray extends VType {
    getTypeParameterCount(): number {
        return 1;
    }

    validate(value: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateArray(value, typeParameters, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomArray(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }

    getName(): string {
        return arrayName;
    }
}
