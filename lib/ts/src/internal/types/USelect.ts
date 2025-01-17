import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateSelect } from '../../internal/validation/ValidateSelect';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { generateRandomSelect } from '../generation/GenerateRandomSelect';

export const select: string = 'Object';

export class USelect implements UType {
    types: Record<string, UType>;
    possibleSelects: Record<string, any>;

    constructor(types: Record<string, UType>, possibleSelects: Record<string, any>) {
        this.types = types;
        this.possibleSelects = possibleSelects;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(
        givenObj: any,
        select: Record<string, any> | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateSelect(givenObj, fn, this.possibleSelects);
    }

    generateRandomValue(ctx: GenerateContext): any {
        return generateRandomSelect(this.possibleSelects, ctx);
    }

    getName(): string {
        return select;
    }
}
