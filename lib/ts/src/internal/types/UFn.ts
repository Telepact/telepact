import { RandomGenerator } from '../../RandomGenerator';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { UUnion } from '../../internal/types/UUnion';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { generateRandomFn } from '../../internal/generation/GenerateRandomFn';

const FN_NAME = 'Object';

export class UFn extends UType {
    name: string;
    call: UUnion;
    result: UUnion;
    errorsRegex: string;
    inheritedErrors: string[] = [];

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
    ): ValidationFailure[] {
        return this.call.validate(value, select, fn, typeParameters);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeOptionalFields: boolean,
        randomizeOptionalFields: boolean,
        typeParameters: UTypeDeclaration[],
        randomGenerator: RandomGenerator,
    ): any {
        return generateRandomFn(
            blueprintValue,
            useBlueprintValue,
            includeOptionalFields,
            randomizeOptionalFields,
            randomGenerator,
            this.call.cases,
        );
    }

    getName(): string {
        return FN_NAME;
    }
}
