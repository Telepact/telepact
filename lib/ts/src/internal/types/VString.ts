import { VTypeDeclaration } from './VTypeDeclaration';
import { ValidationFailure } from '../validation/ValidationFailure';
import { VType } from './VType';
import { validateString } from '../validation/ValidateString';
import { generateRandomString } from '../generation/GenerateRandomString';
import { GenerateContext } from '../generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const stringName: string = 'String';

export class VString extends VType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateString(value);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomString(blueprintValue, useBlueprintValue, ctx);
    }

    getName(): string {
        return stringName;
    }
}
