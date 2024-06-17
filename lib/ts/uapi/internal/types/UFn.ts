import { RandomGenerator } from 'uapi/RandomGenerator';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { UUnion } from 'uapi/internal/types/UUnion';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UType } from 'uapi/internal/types/UType';
import { generateRandomFn } from 'uapi/internal/generation/GenerateRandomFn';

const FN_NAME = 'Object';

export class UFn extends UType {
    name: string;
    call: UUnion;
    result: UUnion;
    errorsRegex: string;

    constructor(name: string, call: UUnion, output: UUnion, errorsRegex: string) {
        super();
        this.name = name;
        this.call = call;
        this.result = output;
        this.errorsRegex = errorsRegex;
    }

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
        return this.call.validate(value, select, fn, typeParameters, generics);
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
        return generateRandomFn(
            blueprintValue,
            useBlueprintValue,
            includeOptionalFields,
            randomizeOptionalFields,
            typeParameters,
            generics,
            randomGenerator,
            this.call.cases,
        );
    }

    getName(generics: UTypeDeclaration[]): string {
        return FN_NAME;
    }
}
