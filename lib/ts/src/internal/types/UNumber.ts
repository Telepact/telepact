import { RandomGenerator } from '../../RandomGenerator';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateNumber } from '../../internal/validation/ValidateNumber';
import { generateRandomNumber } from '../../internal/generation/GenerateRandomNumber';

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
    ): ValidationFailure[] {
        return validateNumber(value);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeOptionalFields: boolean,
        randomizeOptionalFields: boolean,
        typeParameters: UTypeDeclaration[],
        randomGenerator: RandomGenerator,
    ): any {
        return generateRandomNumber(blueprintValue, useBlueprintValue, randomGenerator);
    }

    getName(): string {
        return numberName;
    }
}
