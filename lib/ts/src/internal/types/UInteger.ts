import { RandomGenerator } from '../../RandomGenerator';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { UType } from '../../internal/types/UType';
import { validateInteger } from '../../internal/validation/ValidateInteger';
import { generateRandomInteger } from '../../internal/generation/GenerateRandomInteger';

export const integerName: string = 'Integer';

export class UInteger extends UType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateInteger(value);
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
        return generateRandomInteger(blueprintValue, useBlueprintValue, randomGenerator);
    }

    getName(generics: UTypeDeclaration[]): string {
        return integerName;
    }
}
