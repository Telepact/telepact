import { RandomGenerator } from '../../RandomGenerator';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateSelect } from '../../internal/validation/ValidateSelect';

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
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateSelect(givenObj, select, fn, typeParameters, generics, this.types);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeOptionalFields: boolean,
        randomizeOptionalFields: boolean,
        typeParameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
        randomGenerator: RandomGenerator,
    ): any {
        throw new Error('Not implemented');
    }

    getName(generics: UTypeDeclaration[]): string {
        return select;
    }
}
