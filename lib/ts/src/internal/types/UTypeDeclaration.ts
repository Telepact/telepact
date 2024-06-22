import { RandomGenerator } from 'uapi/RandomGenerator';
import { UType } from 'uapi/internal/types/UType';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { validateValueOfType } from 'uapi/internal/validation/ValidateValueOfType';
import { generateRandomValueOfType } from 'uapi/internal/generation/GenerateRandomValueOfType';

export class UTypeDeclaration {
    type: UType;
    nullable: boolean;
    typeParameters: UTypeDeclaration[];

    constructor(type: UType, nullable: boolean, typeParameters: UTypeDeclaration[]) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateValueOfType(value, select, fn, generics, this.type, this.nullable, this.typeParameters);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeOptionalFields: boolean,
        randomizeOptionalFields: boolean,
        generics: UTypeDeclaration[],
        randomGenerator: RandomGenerator,
    ): any {
        return generateRandomValueOfType(
            blueprintValue,
            useBlueprintValue,
            includeOptionalFields,
            randomizeOptionalFields,
            generics,
            randomGenerator,
            this.type,
            this.nullable,
            this.typeParameters,
        );
    }
}
