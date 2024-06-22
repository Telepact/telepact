import { RandomGenerator } from '../../RandomGenerator';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { UType } from '../../internal/types/UType';
import { validateArray } from '../../internal/validation/ValidateArray';
import { generateRandomArray } from '../../internal/generation/GenerateRandomArray';

export const arrayName = 'Array';

export class UArray extends UType {
    getTypeParameterCount(): number {
        return 1;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateArray(value, select, fn, typeParameters, generics);
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
        return generateRandomArray(
            blueprintValue,
            useBlueprintValue,
            includeOptionalFields,
            randomizeOptionalFields,
            typeParameters,
            generics,
            randomGenerator,
        );
    }

    getName(generics: UTypeDeclaration[]): string {
        return arrayName;
    }
}
