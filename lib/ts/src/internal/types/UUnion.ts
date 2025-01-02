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

    constructor(name: string, cases: { [key: string]: UStruct }, caseIndices: { [key: string]: number }) {
        this.name = name;
        this.cases = cases;
        this.caseIndices = caseIndices;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateUnion(value, select, fn, this.name, this.cases);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeOptionalFields: boolean,
        randomizeOptionalFields: boolean,
        typeParameters: UTypeDeclaration[],
        random: RandomGenerator,
    ): any {
        return generateRandomUnion(
            blueprintValue,
            useBlueprintValue,
            includeOptionalFields,
            randomizeOptionalFields,
            random,
            this.cases,
        );
    }

    getName(): string {
        return unionName;
    }
}
