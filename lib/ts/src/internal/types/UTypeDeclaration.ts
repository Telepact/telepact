import { RandomGenerator } from '../../RandomGenerator';
import { UType } from '../../internal/types/UType';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { validateValueOfType } from '../../internal/validation/ValidateValueOfType';
import { generateRandomValueOfType } from '../../internal/generation/GenerateRandomValueOfType';

export class UTypeDeclaration {
    type: UType;
    nullable: boolean;
    typeParameters: UTypeDeclaration[];

    constructor(type: UType, nullable: boolean, typeParameters: UTypeDeclaration[]) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }

    validate(value: any, select: { [key: string]: any } | null, fn: string | null): ValidationFailure[] {
        return validateValueOfType(value, select, fn, this.type, this.nullable, this.typeParameters);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeOptionalFields: boolean,
        randomizeOptionalFields: boolean,
        randomGenerator: RandomGenerator,
    ): any {
        return generateRandomValueOfType(
            blueprintValue,
            useBlueprintValue,
            includeOptionalFields,
            randomizeOptionalFields,
            randomGenerator,
            this.type,
            this.nullable,
            this.typeParameters,
        );
    }
}
