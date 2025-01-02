import { RandomGenerator } from '../../RandomGenerator';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateObject } from '../../internal/validation/ValidateObject';
import { generateRandomObject } from '../../internal/generation/GenerateRandomObject';

export const objectName: string = 'Object';

export class UObject implements UType {
    getTypeParameterCount(): number {
        return 1;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateObject(value, select, fn, typeParameters);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeOptionalFields: boolean,
        randomizeOptionalFields: boolean,
        typeParameters: UTypeDeclaration[],
        randomGenerator: RandomGenerator,
    ): any {
        return generateRandomObject(
            blueprintValue,
            useBlueprintValue,
            includeOptionalFields,
            randomizeOptionalFields,
            typeParameters,
            randomGenerator,
        );
    }

    getName(): string {
        return objectName;
    }
}
