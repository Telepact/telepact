import { RandomGenerator } from 'uapi/RandomGenerator';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UStruct } from 'uapi/internal/types/UStruct';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { validateUnion } from 'uapi/internal/validation/ValidateUnion';
import { generateRandomUnion } from 'uapi/internal/generation/GenerateRandomUnion';
import { UType } from 'uapi/internal/types/UType';

export const UNION_NAME: string = 'Object';

export class UUnion implements UType {
    name: string;
    cases: { [key: string]: UStruct };
    caseIndices: { [key: string]: number };
    typeParameterCount: number;

    constructor(
        name: string,
        cases: { [key: string]: UStruct },
        caseIndices: { [key: string]: number },
        typeParameterCount: number,
    ) {
        this.name = name;
        this.cases = cases;
        this.caseIndices = caseIndices;
        this.typeParameterCount = typeParameterCount;
    }

    getTypeParameterCount(): number {
        return this.typeParameterCount;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateUnion(value, select, fn, typeParameters, generics, this.name, this.cases);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeOptionalFields: boolean,
        randomizeOptionalFields: boolean,
        typeParameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
        random: RandomGenerator,
    ): any {
        return generateRandomUnion(
            blueprintValue,
            useBlueprintValue,
            includeOptionalFields,
            randomizeOptionalFields,
            typeParameters,
            generics,
            random,
            this.cases,
        );
    }

    getName(generics: UTypeDeclaration[]): string {
        return UNION_NAME;
    }
}
