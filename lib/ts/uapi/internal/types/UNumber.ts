import { RandomGenerator } from 'uapi/RandomGenerator';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UType } from 'uapi/internal/types/UType';
import { validateNumber } from 'uapi/internal/validation/ValidateNumber';
import { generateRandomNumber } from 'uapi/internal/generation/GenerateRandomNumber';

export const numberName: string = 'Number';

export class UNumber extends UType {
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
        return validateNumber(value);
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
        return generateRandomNumber(blueprintValue, useBlueprintValue, randomGenerator);
    }

    getName(generics: UTypeDeclaration[]): string {
        return numberName;
    }
}
