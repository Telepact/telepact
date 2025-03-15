import { VTypeDeclaration } from './VTypeDeclaration';
import { ValidationFailure } from '../validation/ValidationFailure';
import { VType } from './VType';
import { validateSelect } from '../validation/ValidateSelect';
import { GenerateContext } from '../generation/GenerateContext';
import { generateRandomSelect } from '../generation/GenerateRandomSelect';
import { ValidateContext } from '../validation/ValidateContext';

export const select: string = 'Object';

export class VSelect implements VType {
    possibleSelects: Record<string, any> = {};

    getTypeParameterCount(): number {
        return 0;
    }

    validate(givenObj: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateSelect(givenObj, this.possibleSelects, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomSelect(this.possibleSelects, ctx);
    }

    getName(): string {
        return select;
    }
}
