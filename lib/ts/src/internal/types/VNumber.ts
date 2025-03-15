import { ValidationFailure } from '../validation/ValidationFailure';
import { VType } from './VType';
import { validateNumber } from '../validation/ValidateNumber';
import { generateRandomNumber } from '../generation/GenerateRandomNumber';
import { GenerateContext } from '../generation/GenerateContext';
import { VTypeDeclaration } from './VTypeDeclaration';
import { ValidateContext } from '../validation/ValidateContext';

export const numberName: string = 'Number';

export class VNumber extends VType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateNumber(value);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomNumber(blueprintValue, useBlueprintValue, ctx);
    }

    getName(): string {
        return numberName;
    }
}
