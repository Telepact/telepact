import { RandomGenerator } from 'uapi/RandomGenerator';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UType } from 'uapi/internal/types/UType';

export class UGeneric extends UType {
    public index: number;

    constructor(index: number) {
        super();
        this.index = index;
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
        const typeDeclaration = generics[this.index];
        return typeDeclaration.validate(value, select, fn, []);
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
        const genericTypeDeclaration = generics[this.index];
        return genericTypeDeclaration.generateRandomValue(
            blueprintValue,
            useBlueprintValue,
            includeOptionalFields,
            randomizeOptionalFields,
            [],
            randomGenerator,
        );
    }

    getName(generics: UTypeDeclaration[]): string {
        const typeDeclaration = generics[this.index];
        return typeDeclaration.type.getName(generics);
    }
}
