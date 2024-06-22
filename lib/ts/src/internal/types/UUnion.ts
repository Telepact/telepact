import { RandomGenerator } from '../../RandomGenerator';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UStruct } from '../../internal/types/UStruct';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { validateUnion } from '../../internal/validation/ValidateUnion';
import { generateRandomUnion } from '../../internal/generation/GenerateRandomUnion';
import { UType } from '../../internal/types/UType';

export const unionName: string = 'Object';

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
        return unionName;
    }
}
