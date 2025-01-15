import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateSelect } from '../../internal/validation/ValidateSelect';
import { GenerateContext } from '../../internal/generation/GenerateContext';

export type USelectTypes = Record<string, UType>;

export const select: string = 'Object';

export class USelect implements UType {
    types: USelectTypes;

    constructor(types: USelectTypes) {
        this.types = types;
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
        return validateSelect(givenObj, select, fn, this.types);
    }

    generateRandomValue(ctx: GenerateContext): any {
        throw new Error('Not implemented');
    }

    getName(): string {
        return select;
    }
}
